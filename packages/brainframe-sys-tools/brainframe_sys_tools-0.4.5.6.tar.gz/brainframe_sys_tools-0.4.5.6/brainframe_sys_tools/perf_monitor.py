#!/usr/bin/env python3
import time
from datetime import datetime
import os
import psutil
import subprocess
import re
import json
import threading
import sys
import logging
import argparse
# Platform-specific modules for non-blocking keyboard input
try:
    import tty
    import termios
    import select
except ImportError:
    # This will be handled for non-posix systems like Windows
    pass

from typing import List, Dict, Optional, Tuple

try:
    from .command_utils import command, subcommand_parse_args, by_name
except ImportError:
    from command_utils import command, subcommand_parse_args, by_name

try:
    import docker
    from docker.errors import DockerException
    import requests
except ImportError:
    docker = None

HIGH_MEMORY_THRESHOLD_PERCENT = 95.0

class PerfMonitor:
    """
    A modular class to fetch system resource usage statistics. It runs
    background threads for continuous iGPU and keyboard monitoring.
    """

    def __init__(self):
        """Initializes the monitor and starts background threads."""
        self._igpu_usage = 0.0
        self._igpu_last_updated = 0.0
        self._igpu_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._cpu_count = psutil.cpu_count(logical=True)

        log_path = '.'
        if os.path.isdir(log_path) is not True:
            print(f"{log_path} is invalid!")
            exit(1)
        self.time_0 = datetime.now()
        log_ts = str(log_path) + f"/{self.time_0.isoformat()}"

        self.log_file_name = f"{log_ts}_perf_monitor.log"

        self._previous_logged_top_pids = []

        self._setup_logging()

        # daemon=True ensures threads will exit when the main program does
        self._igpu_thread = threading.Thread(target=self._igpu_monitor_thread, daemon=True)
        self._igpu_thread.start()

        self._keyboard_thread = threading.Thread(target=self._keyboard_listener_thread, daemon=True)
        self._keyboard_thread.start()

    def _setup_logging(self):
        """Sets up the CSV logger."""
        self._logger = logging.getLogger('SystemMonitorLogger')
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        handler = logging.FileHandler(self.log_file_name, mode='w')
        self._logger.addHandler(handler)


    def stop(self):
        """Signals all monitoring threads to stop."""
        self._stop_event.set()

    def _keyboard_listener_thread(self):
        """
        A background thread that listens for the 'q' key to stop the monitor.
        """
        if os.name != 'posix':
            return

        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(sys.stdin.fileno())
                while not self._stop_event.is_set():
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        char = sys.stdin.read(1)
                        if char.lower() == 'q':
                            self.stop()
                            break
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except (termios.error, OSError):
            # This will happen when run with sudo, as there is no interactive tty.
            # The thread will simply exit, and the user must use Ctrl+C.
            pass


    def _igpu_monitor_thread(self):
        """
        The background thread function that runs `intel_gpu_top` continuously
        and updates the iGPU usage value by parsing the JSON stream.
        """
        process = None
        while not self._stop_event.is_set():
            try:
                command = ["intel_gpu_top", "-J", "-s", "1000"]
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    stdin=subprocess.DEVNULL
                )

                json_buffer = ""
                brace_count = 0

                for char in iter(lambda: process.stdout.read(1), ''):
                    if self._stop_event.is_set():
                        break

                    if char == '{':
                        if brace_count == 0:
                            json_buffer = ""
                        brace_count += 1

                    if brace_count > 0:
                         json_buffer += char

                    if char == '}':
                        brace_count -= 1

                    if brace_count == 0 and json_buffer:
                        try:
                            data = json.loads(json_buffer)
                            if isinstance(data, list) and data:
                                data = data[0]

                            engines = data.get("engines")
                            if isinstance(engines, dict):
                                render_engine = engines.get("Render/3D")
                                if isinstance(render_engine, dict):
                                    usage = float(render_engine.get("busy", 0.0))
                                    with self._igpu_lock:
                                        self._igpu_usage = usage
                                        self._igpu_last_updated = time.monotonic()
                        except json.JSONDecodeError:
                            pass
                        finally:
                            json_buffer = ""

                process.wait()
                if not self._stop_event.is_set():
                    time.sleep(1)

            except (FileNotFoundError, ValueError):
                break
            finally:
                if process:
                    try:
                        process.kill()
                        process.wait()
                    except OSError:
                        pass

    def get_cpu_usage(self, interval: float = 1) -> float:
        """Returns the system-wide CPU utilization as a percentage."""
        return psutil.cpu_percent(interval=interval)

    def get_cpu_count(self) -> int:
        """Returns the number of logical CPU cores."""
        return self._cpu_count

    def get_igpu_usage(self) -> Optional[float]:
        """
        Returns the latest iGPU usage percentage from the background thread.
        If the data is stale (older than 1.5s), it returns 0.0.
        """
        with self._igpu_lock:
            if time.monotonic() - self._igpu_last_updated > 1.5:
                return 0.0
            return self._igpu_usage

    def get_gpu_usage(self) -> Optional[float]:
        """
        Gets NVIDIA GPU usage by running the `nvidia-smi` command.
        """
        try:
            command = ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
            return None

    def get_memory_usage(self) -> Dict[str, float]:
        """
        Returns a dictionary with detailed memory usage statistics in GB.
        """
        mem = psutil.virtual_memory()
        mem_total_gb = mem.total / (1024**3)
        mem_available_gb = mem.available / (1024**3)

        return {
            "total_gb": mem_total_gb,
            "available_gb": mem_available_gb,
            "used_gb": mem_total_gb - mem_available_gb,
            "percent_used": mem.percent,
            "cache_buffers_gb": (mem.buffers + mem.cached) / (1024**3)
        }

    def get_storage_usage(self) -> Optional[Dict[str, float]]:
        """
        Returns a dictionary with usage statistics for the root filesystem '/'.
        """
        try:
            usage = psutil.disk_usage('/')
            return {
                "total_gb": usage.total / (1024**3),
                "used_gb": usage.used / (1024**3),
                "free_gb": usage.free / (1024**3),
                "percent_used": usage.percent,
            }
        except (FileNotFoundError, Exception):
            return None


    def get_load_average(self) -> Optional[Tuple[float, float, float]]:
        """Returns the system load average over 1, 5, and 15 minutes."""
        try:
            return psutil.getloadavg()
        except (AttributeError, NotImplementedError):
            return None

    def get_temperatures(self) -> Dict[str, Dict[str, Optional[float]]]:
        """
        Runs the 'sensors' command to get key hardware temperatures and their
        high/critical thresholds. Returns a dictionary of dictionaries.
        """
        temps = {
            "CPU": {"current": None, "high": None, "crit": None},
            "GPU": {"current": None, "high": None, "crit": None},
            "Board": {"current": None, "high": None, "crit": None},
            "NVMe": {"current": None, "high": None, "crit": None},
        }
        try:
            result = subprocess.run(['sensors'], capture_output=True, text=True, check=False)
            if result.returncode != 0:
                return temps

            current_module = ""
            for line in result.stdout.splitlines():
                if not line.strip() or ":" not in line:
                    if line.strip():
                        current_module = line.strip()
                    continue

                temp_match = re.search(r'\+(\d+\.\d+)°C', line)
                high_match = re.search(r'high\s*=\s*\+(\d+\.\d+)°C', line)
                crit_match = re.search(r'crit\s*=\s*\+(\d+\.\d+)°C', line)

                current_temp = float(temp_match.group(1)) if temp_match else None
                high_temp = float(high_match.group(1)) if high_match else None
                crit_temp = float(crit_match.group(1)) if crit_match else None

                if current_temp is None:
                    continue

                if 'Package id 0:' in line and 'coretemp' in current_module:
                    temps["CPU"] = {"current": current_temp, "high": high_temp, "crit": crit_temp}
                elif 'GPU:' in line and 'thinkpad' in current_module:
                    temps["GPU"] = {"current": current_temp, "high": high_temp, "crit": crit_temp}
                elif 'Composite:' in line and 'nvme' in current_module:
                    temps["NVMe"] = {"current": current_temp, "high": high_temp, "crit": crit_temp}
                elif 'temp1:' in line and 'acpitz' in current_module:
                    temps["Board"] = {"current": current_temp, "high": high_temp, "crit": crit_temp}

            return temps
        except (FileNotFoundError, Exception):
            return temps

    def _get_pid_to_container_map(self) -> Dict[int, str]:
        """
        Builds a mapping from host PID to Docker container name.
        Returns an empty dictionary if Docker is unavailable or fails.
        """
        if docker is None:
            return {}

        pid_map = {}
        try:
            client = docker.APIClient(base_url='unix://var/run/docker.sock', timeout=1)
            if not client.ping():
                return {}

            containers = client.containers()
            for container_info in containers:
                container_id = container_info['Id']
                container_name = container_info['Names'][0].lstrip('/')
                try:
                    top_data = client.top(container=container_id)
                    if not top_data or 'Processes' not in top_data:
                        continue

                    pids_in_container = [int(p[1]) for p in top_data['Processes']]
                    for pid in pids_in_container:
                        pid_map[pid] = container_name
                except Exception:
                    continue
        except (DockerException, ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            return {}
        return pid_map

    def get_top_memory_processes(self) -> List[Dict]:
        """
        Gets a list of the top 5 memory-consuming processes, sorted by
        Resident Set Size (RSS). It also includes Unique Set Size (USS)
        if it's accessible.
        """
        pid_to_container = self._get_pid_to_container_map()
        
        container_stats = {}
        host_processes = []

        for p in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_full_info', 'cmdline']):
            try:
                # --- Get RSS (Reliable) ---
                mem_info = p.info['memory_info']
                if not mem_info or not mem_info.rss:
                    continue
                
                pid = p.info['pid']
                rss_mb = mem_info.rss / (1024**2)

                # --- Get USS (May fail due to permissions) ---
                uss_mb = None
                try:
                    if p.info['memory_full_info'] and hasattr(p.info['memory_full_info'], 'uss'):
                        uss_mb = p.info['memory_full_info'].uss / (1024**2)
                except (psutil.AccessDenied, AttributeError):
                    # Silently ignore if we can't get USS, uss_mb will remain None
                    pass

                proc_name = ' '.join(p.info['cmdline']) if p.info['cmdline'] else p.info['name']
                container_name = pid_to_container.get(pid)

                if container_name:
                    if container_name not in container_stats:
                        container_stats[container_name] = {
                            'name': container_name,
                            'rss_mb': 0,
                            'type': 'container',
                            'processes': []
                        }
                    container_stats[container_name]['rss_mb'] += rss_mb
                    container_stats[container_name]['processes'].append({
                        'pid': pid,
                        'name': proc_name,
                        'rss_mb': rss_mb,
                        'uss_mb': uss_mb
                    })
                else:
                    if 'perf_monitor.py' in proc_name or sys.argv[0] in proc_name:
                        continue
                    
                    host_processes.append({
                        'pid': pid,
                        'full_cmd': proc_name,
                        'rss_mb': rss_mb,
                        'uss_mb': uss_mb,
                        'type': 'process'
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if docker:
            try:
                client = docker.from_env(timeout=1)
                for name, stats in container_stats.items():
                    try:
                        container_obj = client.containers.get(name)
                        container_id = container_obj.id
                        
                        base_cgroup_path = f"/sys/fs/cgroup/system.slice/docker-{container_id}.scope"
                        if not os.path.isdir(base_cgroup_path):
                            base_cgroup_path = f"/sys/fs/cgroup/memory/docker/{container_id}"
                            if not os.path.isdir(base_cgroup_path):
                                continue
                        
                        # Check for cgroup v2 file first, then fall back to v1
                        mem_v2_file = os.path.join(base_cgroup_path, 'memory.current')
                        mem_v1_file = os.path.join(base_cgroup_path, 'memory.usage_in_bytes')

                        total_bytes = None
                        if os.path.exists(mem_v2_file):
                            with open(mem_v2_file, 'r') as f:
                                content = f.read().strip()

                                if content.isdigit():
                                    total_bytes = int(content)
                        elif os.path.exists(mem_v1_file):
                            with open(mem_v1_file, 'r') as f:
                                total_bytes = int(f.read().strip())
                        
                        if total_bytes is not None:
                            stats['cgroup_total_mb'] = total_bytes / (1024**2)

                    except (DockerException, FileNotFoundError, IOError):
                        continue
            except DockerException:
                pass
        
        for stats in container_stats.values():
            sorted_procs = sorted(stats['processes'], key=lambda x: x['rss_mb'], reverse=True)
            stats['process_count'] = len(stats['processes'])
            stats['top_processes'] = sorted_procs[:3]
            del stats['processes']

        combined_list = list(container_stats.values()) + host_processes
        return sorted(combined_list, key=lambda x: x.get('cgroup_total_mb', x['rss_mb']), reverse=True)[:5]

def log_top_processes(logger: logging.Logger, prefix: str, processes: List[Dict]):
    """Helper function to log the top 5 processes with RSS and USS."""
    if processes:
        # Define column widths
        rss_col_width = 24
        uss_col_width = 12
        separator_width = 3
        combined_width = rss_col_width + separator_width + uss_col_width

        logger.info("")
        logger.info(f"{prefix}: Top 5 memory consumers:")
        logger.info(f"   {'PID':<8} | {'RSS (Cgroup)':<{rss_col_width}} | {'USS':>{uss_col_width}} | Command")

        for i, proc in enumerate(processes):
            if proc.get('type') == 'container':
                pid_str = "-"
                
                rss_part = f"{proc['rss_mb']:>7.2f} MB"
                cgroup_total_mb = proc.get('cgroup_total_mb')
                cgroup_part = f"{cgroup_total_mb:.2f} MB" if cgroup_total_mb is not None else "N/A"
                rss_and_cgroup_str = f"{rss_part} ({cgroup_part})"
                
                count = proc.get('process_count', 0)
                cmd_str = f"Container: {proc['name']} ({count} processes)"
                
                logger.info(f"{i+1}. {pid_str:<8} | {rss_and_cgroup_str:<{combined_width}} | {cmd_str}")
                
                for j, sub_proc in enumerate(proc.get('top_processes', [])):
                    prefix_char = "└─" if j == len(proc['top_processes']) - 1 else "├─"
                    sub_pid_str = sub_proc['pid']
                    sub_rss_str = f"{sub_proc['rss_mb']:>7.2f} MB"
                    sub_uss_mb = sub_proc.get('uss_mb')
                    sub_uss_str = f"{sub_uss_mb:>7.2f} MB" if sub_uss_mb is not None else " "
                    
                    prefixed_sub_cmd = f"{prefix_char} {sub_proc['name']}"

                    logger.info(f"   {str(sub_pid_str):<8} | {sub_rss_str:<{rss_col_width}} | {sub_uss_str:>{uss_col_width}} | {prefixed_sub_cmd}")
            else:
                pid_str = proc['pid']
                rss_str = f"{proc['rss_mb']:>7.2f} MB"
                uss_mb = proc.get('uss_mb')
                uss_str = f"{uss_mb:>7.2f} MB" if uss_mb is not None else " "
                cmd_str = proc['full_cmd']
                
                logger.info(f"{i+1}. {str(pid_str):<8} | {rss_str:<{rss_col_width}} | {uss_str:>{uss_col_width}} | {cmd_str}")

@command("perf-monitor")
def perf_monitor(is_command=True):
    """Main function to run the live performance monitor as a standalone script."""
    parser = argparse.ArgumentParser(description="A system resource monitor.")
    parser.add_argument(
        "--memory",
        default=True,
        action="store_true",
        help="Always display the top memory-consuming processes."
    )
    args = subcommand_parse_args(parser, is_command)

    monitor = PerfMonitor()

    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    start_time = time.monotonic()
    
    try:
        log_top_processes(monitor._logger, "[START]", monitor.get_top_memory_processes())
        
        while not monitor._stop_event.is_set():
            cpu_percent = monitor.get_cpu_usage(interval=0.1)
            cpu_count = monitor.get_cpu_count()
            igpu_percent = monitor.get_igpu_usage()
            gpu_percent = monitor.get_gpu_usage()
            mem_stats = monitor.get_memory_usage()
            storage_stats = monitor.get_storage_usage()
            load_avg = monitor.get_load_average()
            temps = monitor.get_temperatures()

            is_oom = mem_stats["percent_used"] > HIGH_MEMORY_THRESHOLD_PERCENT

            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            log_entry = (
                f"{ts}] CPU: {cpu_percent:.2f}% | "
                f"Mem: {mem_stats['used_gb']:.2f}/{mem_stats['total_gb']:.2f}GB ({mem_stats['percent_used']:.1f}%)"
            )
            monitor._logger.info(log_entry)

            if args.memory or is_oom:
                top_memory_procs = monitor.get_top_memory_processes()
                
                if is_oom:
                    current_consumers = [p.get('pid', p.get('name')) for p in top_memory_procs]
                    if current_consumers != monitor._previous_logged_top_pids:
                        log_top_processes(monitor._logger, f"CRITICAL MEMORY {HIGH_MEMORY_THRESHOLD_PERCENT}% USED", top_memory_procs)
                        monitor._previous_logged_top_pids = current_consumers
                else:
                    monitor._previous_logged_top_pids = []

            clear_screen()

            uptime_seconds = int(time.monotonic() - start_time)
            uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))
            current_time_str = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"                             {current_time_str} Uptime {uptime_str}")

            cpu_bar = '█' * int(40 * cpu_percent / 100) + '-' * (40 - int(40 * cpu_percent / 100))
            print(f"CPU Usage  : |{cpu_bar}| {cpu_percent:.2f}%")
            load_str = f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f} / {cpu_count} Cores" if load_avg else ""
            print(f"              Load Avg {load_str} (1, 5, 15 min)")

            mem_bar = '█' * int(40 * mem_stats["percent_used"] / 100) + '-' * (40 - int(40 * mem_stats["percent_used"] / 100))
            print(f"Mem (Used) : |{mem_bar}| {mem_stats['percent_used']:.2f}%")

            # Cache/Buff: {mem_stats['cache_buffers_gb']:.2f}G | Available: {mem_stats['available_gb']:.2f}G
            print(f"              Used: {mem_stats['used_gb']:.2f}G / Total: {mem_stats['total_gb']:.2f}G")

            if storage_stats:
                storage_bar = '█' * int(40 * storage_stats['percent_used'] / 100) + '-' * (40 - int(40 * storage_stats['percent_used'] / 100))
                print(f"Storage /  : |{storage_bar}| {storage_stats['percent_used']:.2f}%")
                print(f"              Used: {storage_stats['used_gb']:.2f}G / Total: {storage_stats['total_gb']:.2f}G")

            if igpu_percent is not None:
                igpu_bar = '█' * int(40 * igpu_percent / 100) + '-' * (40 - int(40 * igpu_percent / 100))
                print(f"iGPU Usage : |{igpu_bar}| {igpu_percent:.2f}%")

            if gpu_percent is not None:
                gpu_bar = '█' * int(40 * gpu_percent / 100) + '-' * (40 - int(40 * gpu_percent / 100))
                print(f"GPU Usage  : |{gpu_bar}| {gpu_percent:.2f}%")

            print()

            headers = ["CPU", "GPU", "Board (ACPI)", "NVMe"]
            keys    = ["CPU", "GPU", "Board", "NVMe"]
            values  = []

            for key in keys:
                temp_data = temps.get(key)
                value_str = "N/A"
                if temp_data and temp_data['current'] is not None:
                    value_str = f"{temp_data['current']:.1f}°C"
                    details = []
                    if temp_data['high'] is not None:
                        details.append(f"h={temp_data['high']:.1f}")
                    if temp_data['crit'] is not None:
                        details.append(f"c={temp_data['crit']:.1f}")
                    if details:
                        value_str += f" ({','.join(details)})"
                values.append(value_str)

            widths = [max(len(h), len(v)) for h, v in zip(headers, values)]

            header_line_parts = [f"{h:<{w}}" for h, w in zip(headers, widths)]
            value_line_parts  = [f"{v:<{w}}" for v, w in zip(values, widths)]

            print(" | ".join(header_line_parts))
            print(" | ".join(value_line_parts))
            
            process_section_header = "Top 5 Memory Consumers (Sorted by Process RSS):"
            process_lines_to_print = []

            if args.memory or is_oom:
                # Prepend the warning banner if needed
                if is_oom:
                    process_section_header = f"CRITICAL MEMORY {HIGH_MEMORY_THRESHOLD_PERCENT}% USED: " + process_section_header
 
                process_lines_to_print.append(process_section_header.strip())
                process_lines_to_print.append(f"   {'PID':<8} | {'RSS (Cgroup)':<12} | {'USS':>12} | Command")
                if top_memory_procs:
                    for i, proc in enumerate(top_memory_procs):
                        if proc.get('type') == 'container':
                            pid_str = "-"
                            uss_str = " "
                            
                            rss_part = f"{proc['rss_mb']:>9.2f} MB"
                            cgroup_total_mb = proc.get('cgroup_total_mb')
                            if cgroup_total_mb:
                                cgroup_total_str = f"{cgroup_total_mb:.2f} MB"
                            else:
                                cgroup_total_str = f" MB"

                            rss_and_total_str = f"{rss_part} ({cgroup_total_str})"
                            
                            count = proc.get('process_count', 0)
                            top_procs = proc.get('top_processes', [])
                            
                            raw_name = proc['name']
                            truncated_name = (raw_name[:20] + '..') if len(raw_name) > 22 else raw_name
                            if count > len(top_procs):
                                summary_text = f"({count} processes, top {len(top_procs)} shown)"
                            else:
                                summary_text = f"({count} processes)"
                            
                            cmd_str = f"docker top {truncated_name} -o pid,rss,cmd {summary_text}"
                            
                            process_lines_to_print.append(f"{i+1}. {str(pid_str):<8} | {rss_and_total_str:<27} | {cmd_str}")

                            for j, sub_proc in enumerate(top_procs):
                                is_last = (j == len(top_procs) - 1)
                                prefix = "└─" if is_last else "├─"
                                
                                sub_pid_str = sub_proc['pid']
                                sub_rss_str = f"{sub_proc['rss_mb']:>7.2f} MB"
                                sub_uss_mb = sub_proc.get('uss_mb')
                                sub_uss_str = f"{sub_uss_mb:>7.2f} MB" if sub_uss_mb is not None else " "
                                
                                prefixed_sub_cmd = f"{prefix} {sub_proc['name']}"
                                sub_cmd_truncated = (prefixed_sub_cmd[:65] + '..') if len(prefixed_sub_cmd) > 67 else prefixed_sub_cmd
                                process_lines_to_print.append(f"   {str(sub_pid_str):<8} | {sub_rss_str:>12} | {sub_uss_str:>12} | {sub_cmd_truncated}")

                        else:
                            pid_str = proc['pid']
                            rss_str = f"{proc['rss_mb']:>9.2f} MB"
                            uss_mb = proc.get('uss_mb')
                            uss_str = f"{uss_mb:>7.2f} MB" if uss_mb is not None else " "
                            cmd_str = proc['full_cmd']
                            cmd_str_truncated = (cmd_str[:70] + '..') if len(cmd_str) > 72 else cmd_str
                            process_lines_to_print.append(f"{i+1}. {str(pid_str):<8} | {rss_str:<12} | {uss_str:>12} | {cmd_str_truncated}")
                else:
                    process_lines_to_print.append("No running processes or containers found.")
            
            if process_lines_to_print:
                print("\n" + "\n".join(process_lines_to_print))

            print("\n           sudo is required for iGPU usage access. Press 'q' to exit")

            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting monitor gracefully...")
    finally:
        monitor.stop()
        log_top_processes(monitor._logger, "[STOP]", monitor.get_top_memory_processes())
        print(f"\nLog file '{monitor.log_file_name}' has been created.")

def check_docker_connection() -> Tuple[str, Optional[str]]:
    """
    Checks for Docker availability and configuration issues.

    Returns a tuple of (status, error_message), where status is one of:
    'OK', 'NOT_INSTALLED', 'PERMISSION_ERROR', 'CONNECTION_ERROR'.
    """
    try:
        import docker
        from docker.errors import DockerException
    except ImportError:
        return 'NOT_INSTALLED', None

    try:
        client = docker.from_env(timeout=1)
        client.ping()
        return 'OK', None
    except DockerException as e:
        if 'Permission denied' in str(e):
            return 'PERMISSION_ERROR', str(e)
        else:
            return 'CONNECTION_ERROR', str(e)
    except Exception as e:
        return 'CONNECTION_ERROR', str(e)

if __name__ == "__main__":
    docker_status, error_msg = check_docker_connection()

    if docker_status != 'OK':
        print("--- Docker Integration Warning ---")
        print("Container detection will be disabled due to a configuration issue.")
        print("To fix this, please follow the relevant steps below:\n")

        if docker_status == 'NOT_INSTALLED':
            print("1. Install the Docker SDK for Python:")
            print("   pip install docker")
        
        elif docker_status == 'PERMISSION_ERROR':
            print("1. Add your user to the 'docker' group:")
            print("   sudo usermod -aG docker ${USER}")
            print("\n2. IMPORTANT: You must log out and log back in for this change to take effect.")

        elif docker_status == 'CONNECTION_ERROR':
            print("1. Ensure the Docker daemon is running:")
            print("   sudo systemctl status docker")
            print("\n2. You may have an incompatible version of the Docker SDK. This can happen with")
            print("   very new Docker Engine releases. Try upgrading the library:")
            print("   pip install --upgrade docker")
            print(f"\n   (Error details: {error_msg})")
        
        print("\nContinuing without container monitoring in 5 seconds...")
        time.sleep(5)

    try:
        by_name["perf-monitor"](False)
    except (NameError, KeyError):
        perf_monitor(False)

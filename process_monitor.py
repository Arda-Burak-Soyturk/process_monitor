import psutil
import time
import os
from datetime import datetime
from colorama import init, Fore, Back, Style
import threading
import msvcrt

# Initialize colorama
init()

# List of processes to exclude
EXCLUDED_PROCESSES = {
    'WmiApSrv.exe',
    'svchost.exe',
    'RuntimeBroker.exe',
    'dwm.exe',
    'csrss.exe',
    'smss.exe',
    'wininit.exe',
    'services.exe',
    'lsass.exe',
    'winlogon.exe',
    'System',
    'Registry',
    'Memory Compression',
    'Secure System',
    'SystemSettings.exe',
    'fontdrvhost.exe',
    'sihost.exe',
    'taskhostw.exe',
    'ctfmon.exe',
    'conhost.exe'
}

def truncate_name(name, max_length=24):
    if len(name) > max_length:
        return name[:max_length-3] + "..."
    return name

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_system_info():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'memory_percent': memory.percent,
        'memory_used': memory.used / (1024 * 1024 * 1024),  # GB
        'memory_total': memory.total / (1024 * 1024 * 1024),  # GB
        'disk_percent': disk.percent,
        'disk_used': disk.used / (1024 * 1024 * 1024),  # GB
        'disk_total': disk.total / (1024 * 1024 * 1024),  # GB
        'process_count': len(psutil.pids())
    }

def get_process_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'create_time', 
                                   'num_threads', 'nice', 'cwd', 'cmdline', 'ppid']):
        try:
            pinfo = proc.info
            # Skip excluded processes and processes using less than 1MB of memory
            if (pinfo['name'] in EXCLUDED_PROCESSES or 
                pinfo['memory_info'].rss < 1024 * 1024):  # Less than 1MB
                continue
                
            processes.append({
                'pid': pinfo['pid'],
                'name': truncate_name(pinfo['name']),
                'full_name': pinfo['name'],  # Keep the full name for detailed view
                'memory': pinfo['memory_info'].rss / 1024,  # Convert to KB
                'create_time': datetime.fromtimestamp(pinfo['create_time']).strftime('%H:%M:%S') if pinfo['create_time'] else 'N/A',
                'threads': pinfo['num_threads'],
                'priority': pinfo['nice'],
                'cwd': pinfo['cwd'] if pinfo['cwd'] else 'N/A',
                'cmdline': ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else 'N/A',
                'ppid': pinfo['ppid']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return sorted(processes, key=lambda x: x['memory'], reverse=True)

def format_memory(memory_kb):
    if memory_kb > 1024 * 1024:  # More than 1GB
        return f"{memory_kb/1024/1024:.1f} GB"
    elif memory_kb > 1024:  # More than 1MB
        return f"{memory_kb/1024:.1f} MB"
    else:
        return f"{memory_kb:.0f} KB"

def create_progress_bar(percent, width=20):
    filled = int(width * percent / 100)
    bar = '█' * filled + '░' * (width - filled)
    if percent > 80:
        color = Fore.RED
    elif percent > 60:
        color = Fore.YELLOW
    else:
        color = Fore.GREEN
    return f"{color}{bar}{Style.RESET_ALL} {percent:>3.0f}%"

def display_system_info(sys_info):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}System Monitor{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    
    # Memory and Disk
    print(f"{Fore.WHITE}Memory Usage: {create_progress_bar(sys_info['memory_percent'])} ({sys_info['memory_used']:.1f}GB / {sys_info['memory_total']:.1f}GB)")
    print(f"{Fore.WHITE}Disk Usage:   {create_progress_bar(sys_info['disk_percent'])} ({sys_info['disk_used']:.1f}GB / {sys_info['disk_total']:.1f}GB)")
    print(f"{Fore.WHITE}Processes:    {sys_info['process_count']}")
    print(f"{Fore.CYAN}{'-' * 70}{Style.RESET_ALL}")

def display_processes(processes):
    # Print header with colors
    print(f"{Fore.CYAN}{Style.BRIGHT}{'Process Name':<24} {'PID':<8} {'PPID':<8} {'Memory':<12} {'Threads':<8}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-' * 70}{Style.RESET_ALL}")
    
    # Print processes with alternating colors
    for i, proc in enumerate(processes):
        # Alternate between white and light gray for better readability
        color = Fore.WHITE if i % 2 == 0 else Fore.LIGHTBLACK_EX
        
        # Highlight processes using more than 1GB of memory
        if proc['memory'] > 1024 * 1024:
            memory_color = Fore.RED
        elif proc['memory'] > 512 * 1024:  # More than 512MB
            memory_color = Fore.YELLOW
        else:
            memory_color = color

        print(f"{color}{proc['name']:<24} {proc['pid']:<8} {proc['ppid']:<8} {memory_color}{format_memory(proc['memory']):<12} {proc['threads']:<8}{Style.RESET_ALL}")

def display_process_details(process):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Process Details:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-' * 50}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Name: {Fore.GREEN}{process['full_name']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}PID: {Fore.GREEN}{process['pid']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Parent PID: {Fore.GREEN}{process['ppid']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Memory Usage: {Fore.GREEN}{format_memory(process['memory'])}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Threads: {Fore.GREEN}{process['threads']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Priority: {Fore.GREEN}{process['priority']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Start Time: {Fore.GREEN}{process['create_time']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Working Directory: {Fore.GREEN}{process['cwd']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Command Line: {Fore.GREEN}{process['cmdline']}{Style.RESET_ALL}")

def display_commands():
    print(f"\n{Fore.GREEN}Commands:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}k <PID>  {Style.RESET_ALL}- Kill process")
    print(f"{Fore.CYAN}s <name> {Style.RESET_ALL}- Search for process")
    print(f"{Fore.CYAN}d <PID>  {Style.RESET_ALL}- Show detailed process info")
    print(f"{Fore.CYAN}r        {Style.RESET_ALL}- Refresh now")
    print(f"{Fore.CYAN}q        {Style.RESET_ALL}- Quit")
    print(f"{Fore.CYAN}h        {Style.RESET_ALL}- Show this help")

def kill_process(pid):
    try:
        # First check if process exists
        if not psutil.pid_exists(pid):
            print(f"{Fore.RED}Error: Process with PID {pid} does not exist{Style.RESET_ALL}")
            return

        process = psutil.Process(pid)
        process_name = process.name()
        
        # Try to terminate the process
        try:
            process.terminate()
            print(f"{Fore.GREEN}Successfully terminated process: {process_name} (PID: {pid}){Style.RESET_ALL}")
        except psutil.AccessDenied:
            print(f"{Fore.RED}Error: Access denied to terminate process {process_name} (PID: {pid}){Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Try running the program as administrator{Style.RESET_ALL}")
    except psutil.NoSuchProcess:
        print(f"{Fore.RED}Error: Process {pid} no longer exists{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

def search_processes(processes, search_term):
    search_term = search_term.lower()
    found = False
    for proc in processes:
        if search_term in proc['full_name'].lower():
            found = True
            print(f"{Fore.GREEN}Found: {proc['full_name']} (PID: {proc['pid']}){Style.RESET_ALL}")
    if not found:
        print(f"{Fore.YELLOW}No processes found matching '{search_term}'{Style.RESET_ALL}")

def get_pid_input():
    while True:
        try:
            pid_input = input(f"{Fore.CYAN}Enter PID: {Style.RESET_ALL}").strip()
            if not pid_input:  # If user just pressed Enter
                print(f"{Fore.YELLOW}Operation cancelled{Style.RESET_ALL}")
                return None
            pid = int(pid_input)
            if pid <= 0:
                print(f"{Fore.RED}Error: PID must be a positive number{Style.RESET_ALL}")
                continue
            return pid
        except ValueError:
            print(f"{Fore.RED}Error: Please enter a valid number for PID{Style.RESET_ALL}")

def main():
    print(f"{Fore.GREEN}{Style.BRIGHT}Process Monitor - Press Ctrl+C to exit{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Updating every 30 seconds...{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}Filtered out common Windows background processes{Style.RESET_ALL}")
    
    display_commands()
    
    try:
        while True:
            clear_screen()
            sys_info = get_system_info()
            display_system_info(sys_info)
            processes = get_process_info()
            display_processes(processes)
            display_commands()
            
            # Check for user input without blocking
            if msvcrt.kbhit():
                cmd = msvcrt.getch().decode().lower()
                if cmd == 'q':
                    break
                elif cmd == 'h':
                    display_commands()
                elif cmd == 'r':
                    continue
                elif cmd == 'k':
                    pid = get_pid_input()
                    if pid is not None:
                        kill_process(pid)
                elif cmd == 's':
                    search_term = input(f"{Fore.CYAN}Enter process name to search: {Style.RESET_ALL}")
                    search_processes(processes, search_term)
                elif cmd == 'd':
                    pid = get_pid_input()
                    if pid is not None:
                        for proc in processes:
                            if proc['pid'] == pid:
                                display_process_details(proc)
                                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                                break
                        else:
                            print(f"{Fore.RED}Process with PID {pid} not found in current list{Style.RESET_ALL}")
            
            # Show countdown
            for i in range(30, 0, -1):
                if msvcrt.kbhit():  # Check for user input during countdown
                    break
                print(f"\r{Fore.CYAN}Next update in {i} seconds...{Style.RESET_ALL}", end='')
                time.sleep(1)
            print("\r" + " " * 50 + "\r", end='')  # Clear the countdown line
            
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}Exiting process monitor...{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 
# Windows Process Monitor

A command-line based interactive system and process monitor for Windows, developed in Python. It displays detailed information about memory, disk usage, and running processes in real time. Built with `psutil`, `colorama`, and `msvcrt` to enhance interactivity and terminal visuals.

---

## Features

- Real-time system resource monitoring (RAM, Disk)
- Lists active processes excluding essential Windows services
- Highlights processes using high memory
- User commands for:
  - Killing processes by PID
  - Searching for process by name
  - Viewing detailed process information
- Interactive input with `msvcrt` for Windows terminal (non-blocking)
- Color-coded UI with progress bars and table views
- Auto-refreshes every 30 seconds

---

## Requirements

- Python 3.8+
- Windows OS (due to use of `msvcrt`)
- Dependencies:
  - `psutil`
  - `colorama`

Install dependencies via:

```bash
pip install psutil colorama

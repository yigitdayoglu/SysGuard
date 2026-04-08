import psutil


def get_running_processes():
    processes = []

    try:
        for proc in psutil.process_iter(["pid", "name", "exe", "cmdline", "ppid", "create_time"]):
            try:
                info = proc.info
                parent_name = None
                try:
                    parent = proc.parent()
                    parent_name = parent.name() if parent else None
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    parent_name = None

                processes.append({
                    "pid": info.get("pid"),
                    "name": info.get("name"),
                    "exe": info.get("exe"),
                    "cmdline": info.get("cmdline"),
                    "ppid": info.get("ppid"),
                    "parent_name": parent_name,
                    "create_time": info.get("create_time"),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except (psutil.Error, PermissionError):
        return []

    return processes

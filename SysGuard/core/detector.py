def list_to_dict(items, key):
    return {item[key]: item for item in items if key in item and item[key] is not None}


def detect_changes(baseline, current):
    events = []

    baseline_files = list_to_dict(baseline.get("files", []), "path")
    current_files = list_to_dict(current.get("files", []), "path")

    baseline_processes = list_to_dict(baseline.get("processes", []), "pid")
    current_processes = list_to_dict(current.get("processes", []), "pid")

    baseline_startup = list_to_dict(baseline.get("startup_items", []), "path")
    current_startup = list_to_dict(current.get("startup_items", []), "path")

    for path in current_files:
        if path not in baseline_files:
            events.append({
                "type": "new_file",
                "target": path,
                "size": current_files[path].get("size"),
                "modified_time": current_files[path].get("modified_time"),
            })
        else:
            old = baseline_files[path]
            new = current_files[path]

            if old["size"] != new["size"] or old["modified_time"] != new["modified_time"]:
                events.append({
                    "type": "modified_file",
                    "target": path,
                    "size": new.get("size"),
                    "modified_time": new.get("modified_time"),
                })

    for path in baseline_files:
        if path not in current_files:
            events.append({
                "type": "deleted_file",
                "target": path,
            })

    for pid in current_processes:
        if pid not in baseline_processes:
            process = current_processes[pid]
            events.append({
                "type": "new_process",
                "target": process.get("name", str(pid)),
                "pid": pid,
                "exe": process.get("exe"),
                "cmdline": process.get("cmdline"),
                "ppid": process.get("ppid"),
                "parent_name": process.get("parent_name"),
                "create_time": process.get("create_time"),
            })

    for pid in baseline_processes:
        if pid not in current_processes:
            process = baseline_processes[pid]
            events.append({
                "type": "terminated_process",
                "target": process.get("name", str(pid)),
                "pid": pid,
                "exe": process.get("exe"),
                "cmdline": process.get("cmdline"),
                "ppid": process.get("ppid"),
                "parent_name": process.get("parent_name"),
                "create_time": process.get("create_time"),
            })

    for path in current_startup:
        if path not in baseline_startup:
            startup_item = current_startup[path]
            events.append({
                "type": "new_startup_item",
                "target": path,
                "label": startup_item.get("label"),
                "program": startup_item.get("program"),
                "program_arguments": startup_item.get("program_arguments"),
                "working_directory": startup_item.get("working_directory"),
                "run_at_load": startup_item.get("run_at_load"),
                "keep_alive": startup_item.get("keep_alive"),
            })

    for path in baseline_startup:
        if path not in current_startup:
            startup_item = baseline_startup[path]
            events.append({
                "type": "removed_startup_item",
                "target": path,
                "label": startup_item.get("label"),
                "program": startup_item.get("program"),
                "program_arguments": startup_item.get("program_arguments"),
                "working_directory": startup_item.get("working_directory"),
                "run_at_load": startup_item.get("run_at_load"),
                "keep_alive": startup_item.get("keep_alive"),
            })

    return events

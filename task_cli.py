#!/usr/bin/env python3
"""
Task Tracker CLI (no external libraries)
Usage examples:
  python task_cli.py add "Buy groceries"
  python task_cli.py update 1 "Buy groceries and cook dinner"
  python task_cli.py delete 1
  python task_cli.py mark-in-progress 1
  python task_cli.py mark-done 1
  python task_cli.py list
  python task_cli.py list done
  python task_cli.py list todo
  python task_cli.py list in-progress
"""

import json
import os
import sys
from datetime import datetime

DB_FILE = "tasks.json"
VALID_STATUSES = {"todo", "in-progress", "done"}


def now_iso() -> str:
    # ISO 8601 with seconds, local time
    return datetime.now().replace(microsecond=0).isoformat()


def print_usage() -> None:
    print(
        "Task Tracker CLI\n"
        "Commands:\n"
        "  add <description>\n"
        "  update <id> <new_description>\n"
        "  delete <id>\n"
        "  mark-in-progress <id>\n"
        "  mark-done <id>\n"
        "  list [todo|in-progress|done]\n"
        "\n"
        "Examples:\n"
        '  python task_cli.py add "Buy groceries"\n'
        '  python task_cli.py update 1 "Buy groceries and cook dinner"\n'
        "  python task_cli.py delete 1\n"
        "  python task_cli.py mark-in-progress 1\n"
        "  python task_cli.py mark-done 1\n"
        "  python task_cli.py list\n"
        "  python task_cli.py list done\n"
    )


def ensure_db_exists() -> None:
    if not os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
        except OSError as e:
            print(f"Error: could not create {DB_FILE}: {e}")
            sys.exit(1)


def load_tasks() -> list[dict]:
    ensure_db_exists()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validate basic structure
        if not isinstance(data, list):
            raise ValueError("Database format invalid (expected a list).")

        # Filter to only dict tasks (defensive)
        tasks = [t for t in data if isinstance(t, dict)]
        return tasks

    except json.JSONDecodeError:
        print(f"Error: {DB_FILE} is not valid JSON. Fix it or delete it and rerun.")
        sys.exit(1)
    except (OSError, ValueError) as e:
        print(f"Error: could not read tasks: {e}")
        sys.exit(1)


def save_tasks(tasks: list[dict]) -> None:
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
    except OSError as e:
        print(f"Error: could not write to {DB_FILE}: {e}")
        sys.exit(1)


def next_id(tasks: list[dict]) -> int:
    max_id = 0
    for t in tasks:
        tid = t.get("id")
        if isinstance(tid, int) and tid > max_id:
            max_id = tid
    return max_id + 1


def parse_id(s: str) -> int:
    try:
        i = int(s)
        if i <= 0:
            raise ValueError
        return i
    except ValueError:
        print("Error: id must be a positive integer.")
        sys.exit(1)


def find_task(tasks: list[dict], task_id: int) -> dict | None:
    for t in tasks:
        if t.get("id") == task_id:
            return t
    return None


def cmd_add(args: list[str]) -> None:
    if len(args) < 1:
        print("Error: missing description.")
        print_usage()
        sys.exit(1)

    description = " ".join(args).strip()
    if not description:
        print("Error: description cannot be empty.")
        sys.exit(1)

    tasks = load_tasks()
    tid = next_id(tasks)
    ts = now_iso()

    task = {
        "id": tid,
        "description": description,
        "status": "todo",
        "createdAt": ts,
        "updatedAt": ts,
    }

    tasks.append(task)
    save_tasks(tasks)
    print(f"Task added successfully (ID: {tid})")


def cmd_update(args: list[str]) -> None:
    if len(args) < 2:
        print("Error: update requires <id> <new_description>.")
        print_usage()
        sys.exit(1)

    task_id = parse_id(args[0])
    new_description = " ".join(args[1:]).strip()
    if not new_description:
        print("Error: new description cannot be empty.")
        sys.exit(1)

    tasks = load_tasks()
    task = find_task(tasks, task_id)
    if not task:
        print(f"Error: task with ID {task_id} not found.")
        sys.exit(1)

    task["description"] = new_description
    task["updatedAt"] = now_iso()
    save_tasks(tasks)
    print(f"Task {task_id} updated successfully.")


def cmd_delete(args: list[str]) -> None:
    if len(args) != 1:
        print("Error: delete requires <id>.")
        print_usage()
        sys.exit(1)

    task_id = parse_id(args[0])
    tasks = load_tasks()

    before = len(tasks)
    tasks = [t for t in tasks if t.get("id") != task_id]
    after = len(tasks)

    if after == before:
        print(f"Error: task with ID {task_id} not found.")
        sys.exit(1)

    save_tasks(tasks)
    print(f"Task {task_id} deleted successfully.")


def set_status(task: dict, status: str) -> None:
    task["status"] = status
    task["updatedAt"] = now_iso()


def cmd_mark_in_progress(args: list[str]) -> None:
    if len(args) != 1:
        print("Error: mark-in-progress requires <id>.")
        print_usage()
        sys.exit(1)

    task_id = parse_id(args[0])
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    if not task:
        print(f"Error: task with ID {task_id} not found.")
        sys.exit(1)

    set_status(task, "in-progress")
    save_tasks(tasks)
    print(f"Task {task_id} marked as in-progress.")


def cmd_mark_done(args: list[str]) -> None:
    if len(args) != 1:
        print("Error: mark-done requires <id>.")
        print_usage()
        sys.exit(1)

    task_id = parse_id(args[0])
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    if not task:
        print(f"Error: task with ID {task_id} not found.")
        sys.exit(1)

    set_status(task, "done")
    save_tasks(tasks)
    print(f"Task {task_id} marked as done.")


def format_task(t: dict) -> str:
    # Defensive gets
    tid = t.get("id", "?")
    status = t.get("status", "?")
    desc = t.get("description", "")
    created = t.get("createdAt", "")
    updated = t.get("updatedAt", "")
    return f"[{tid}] ({status}) {desc}\n    created: {created}\n    updated: {updated}"


def cmd_list(args: list[str]) -> None:
    tasks = load_tasks()

    status_filter = None
    if len(args) == 1:
        status_filter = args[0].strip().lower()
        if status_filter not in VALID_STATUSES:
            print("Error: list status must be one of: todo, in-progress, done")
            sys.exit(1)
    elif len(args) > 1:
        print("Error: list takes at most one optional status.")
        print_usage()
        sys.exit(1)

    if status_filter:
        tasks = [t for t in tasks if t.get("status") == status_filter]

    if not tasks:
        print("No tasks found.")
        return

    # Sort by id for stable display
    tasks_sorted = sorted(tasks, key=lambda x: x.get("id", 10**9))
    for t in tasks_sorted:
        print(format_task(t))


def main() -> None:
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].strip().lower()
    args = sys.argv[2:]

    commands = {
        "add": cmd_add,
        "update": cmd_update,
        "delete": cmd_delete,
        "mark-in-progress": cmd_mark_in_progress,
        "mark-done": cmd_mark_done,
        "list": cmd_list,
    }

    if command not in commands:
        print(f"Error: unknown command '{command}'.")
        print_usage()
        sys.exit(1)

    commands[command](args)


if __name__ == "__main__":
    main()

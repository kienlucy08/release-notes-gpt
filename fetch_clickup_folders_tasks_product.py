import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import re
from collections import defaultdict

# Load API Token
load_dotenv()
token = os.getenv("CLICK_UP_TOKEN")

# CLickup Identifiers
FOLDER_ID = "90116436231"
SPACE_ID = "90110707615"

# Authentication
HEADERS = {
    "Authorization": token
}

# ---------------------- API FUNCTIONS ----------------------

def get_lists_from_folder(folder_id):
    """
    Fetches all lists inside a ClickUp folder.
    """
    url = f"https://api.clickup.com/api/v2/folder/{folder_id}/list"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("lists", [])

def get_sprint_lists(folder_id):
    """Returns only lists that look like sprint folders."""
    all_lists = get_lists_from_folder(folder_id)
    return [lst for lst in all_lists if "sprint" in lst["name"].lower()]

def extract_date_range(list_name):
    """
    Extracts (start_date, end_date) from a sprint list name like: "Sprint 1 (6/1 - 6/14)"
    """
    match = re.search(r"\((\d{1,2}/\d{1,2})\s*-\s*(\d{1,2}/\d{1,2})\)", list_name)
    if not match:
        return None, None
    year = datetime.today().year
    start = datetime.strptime(f"{match.group(1)}/{year}", "%m/%d/%Y")
    end = datetime.strptime(f"{match.group(2)}/{year}", "%m/%d/%Y")
    return start, end

def get_tasks_in_list(list_id, debug=False):
    """
    Fetches all tasks from a ClickUp list (paginated), including closed tasks.
    """
    all_tasks = []
    page = 0

    while True:
        url = f"https://api.clickup.com/api/v2/list/{list_id}/task?page={page}&limit=100&include_closed=true"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        tasks = resp.json().get("tasks", [])
        all_tasks.extend(tasks)

        if not tasks or len(tasks) < 100:
            break
        page += 1

    if debug:
        print(f"📦 {len(all_tasks)} tasks from list {list_id}")
    return all_tasks

def get_all_tasks_from_folder_lists(folder_id, debug=False):
    """
    Fetches all tasks from all lists within a folder.
    """
    all_tasks = []
    lists = get_lists_from_folder(folder_id)
    for lst in lists:
        tasks = get_tasks_in_list(lst["id"], debug=debug)
        all_tasks.extend(tasks)
    print(f"✅ Total {len(all_tasks)} tasks retrieved from folder {folder_id}")
    return all_tasks

def get_all_tasks_with_metadata(folder_id):
    def readable(ts):
        return datetime.fromtimestamp(int(ts)/1000).strftime("%Y-%m-%d %H:%M:%S") if ts else None
    all_tasks = []
    lists = get_lists_from_folder(folder_id)
    for lst in lists:
        list_id = lst["id"]
        list_name = lst["name"]
        tasks = get_tasks_in_list(list_id, list_name)
        all_tasks.extend(tasks)
    return [
        {
            "task_id": t["id"],
            "task_name": t["name"],
            "list_name": list_name,
            "list_id": list_id,
            "date_done": readable(t.get("date_done")),
            "date_closed": readable(t.get("date_closed")),
            "start_date": readable(t.get("start_date")),
            "due_date": readable(t.get("due_date")),
            "date_updated": readable(t.get("date_updated"))
        }
        for t in all_tasks
    ]

# ------------------ LOGIC FUNCTIONS ------------------------

def assign_to_sprint_by_close_date(task, sprint_ranges):
    # Try multiple date fields in priority order
    date_fields = [
        "date_closed",
        "date_done",
        "start_date",
        "due_date",
        "date_updated"
    ]

    for field in date_fields:
        date_str = task.get(field)
        if date_str:
            try:
                close_dt = datetime.fromtimestamp(int(date_str) / 1000)
                break
            except:
                continue
    else:
        # No usable date found
        return None

    for sprint_name, (start_str, end_str) in sprint_ranges.items():
        start_dt = datetime.strptime(start_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=999999)
        if start_dt <= close_dt <= end_dt:
            return sprint_name

    return None

if __name__ == "__main__":
    # 1. Get sprint lists and date ranges
    sprint_lists = get_sprint_lists(FOLDER_ID)
    sprint_ranges = {}

    for sprint in sprint_lists:
        name = sprint["name"]
        start, end = extract_date_range(name)
        if start and end:
            sprint_ranges[name] = (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    # 2. Get all tasks from all lists in the folder
    all_tasks = get_all_tasks_from_folder_lists(FOLDER_ID, debug=False)
    metadata = get_all_tasks_with_metadata(FOLDER_ID)
    for meta in metadata:
        name = meta.get("task_name")
        list_name = meta.get("list_name")
        date_closed = meta.get("date_closed")
        print(f"Name: {name}")
        print(f"List Name: {list_name}")
        print(f"Date Closed: {date_closed}")
        print("-----------------------")

    # 3. Assign tasks to sprints
    sprint_buckets = defaultdict(list)
    for task in all_tasks:
        assigned_sprint = assign_to_sprint_by_close_date(task, sprint_ranges)
        sprint_buckets[assigned_sprint or "Unassigned"].append(task)

    # 4. Print summary
    print("\n📊 Task Distribution by Sprint:")
    for sprint_name in sorted(sprint_buckets):
        print(f"- {sprint_name}: {len(sprint_buckets[sprint_name])} tasks")
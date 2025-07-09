import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import re
from collections import defaultdict

# Load API Token
load_dotenv()
token = os.getenv("CLICK_UP_TOKEN")

# Folder Identifiers
DEV_FOLDER_ID = "90115096402"
PRODUCT_FOLDER_ID = "90116436231"

# Optional lists to pull from
FIELDSYNC_LIST_ID = "901110252032"
FS_WEB_APP_USER_FEEDBACK_ID = "901109641571"

# Known Sprint Label ID -> Name Mapping
CUSTOM_FIELD_ID = "eaec1223-07ff-4ab6-bc9a-10dee0328b0d"
FIELD_ID_TO_SPRINT = {
    "78caf6c8-6ebe-4475-8864-517fb2bc8287" : "Sprint 6 (7/2 - 7/15)",
    "7c5de467-d7ab-4e4a-9b0b-544e083c04e2" : "Sprint 5 (6/18 - 7/1)",
    "38fd6029-d934-4fc3-a06f-8f16eec12a51" : "Sprint 3 (5/14 - 6/3)",
    "7ac74835-3f56-469d-bf88-3232ff36f03a" : "Sprint 1 (4/16 - 4/29)",
    "ce584c56-7a9b-4210-ba0f-a495437d4a9a" : "Sprint 2 (4/30 - 5/13)",
    "81702e1f-2913-4063-a546-1c27d7f5187c" : "Sprint 4 (6/4 - 6/17)"
}

# Authentication headers
HEADERS = {
    "Authorization": token,
    "accept": "application/json"
}

# ---------------------- PRIMARY API FUNCTIONS ----------------------

def get_lists_from_folder(folder_id):
    """
    Fetches all lists inside a ClickUp Folder.

    Args:
        folder_id (str): The ID of the folder.

    Returns:
        list: A list of ClickUp lists.
    """
    url = f"https://api.clickup.com/api/v2/folder/{folder_id}/list"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("lists", [])

def get_sprint_lists(folder_id):
    """
    Returns only lists that look like sprint folders.
    
    Args:
        folder_id (str): The ID of the folder to search.
    
    Returns:
        list: A filtered list of sprint lists
    """
    all_lists = get_lists_from_folder(folder_id)
    return [lst for lst in all_lists if "sprint" in lst["name"].lower()]

def get_tasks_in_list(list_id, debug=False):
    """
    Fetches all tasks from a ClickUp list, including closed tasks and subtasks
    
    Args:
        list_id (str): The ID of the list.
        debug (bool): Whether to print debug info.
    
    Returns:
        list: A list of task dictionaries.
    """
    tasks, page = [], 0
    while True:
        url = f"https://api.clickup.com/api/v2/list/{list_id}/task?page={page}&limit=100&include_closed=true"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        chunk = resp.json().get("tasks", [])
        tasks.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    if debug:
        print(f"Retrieved {len(tasks)} tasks from list {list_id}")
    return tasks

def get_all_tasks_from_folder_lists(folder_id, debug=False):
    """
    Fetches all tasks from all lists within a folder.

    Args:
        folder_id (str): The ID of the folder to search.
        debug (bool): Whether to print debug info.
    
    Returns:
        list: A combined list of tasks across all lists in the folder.
    """
    all_tasks = []
    lists = get_lists_from_folder(folder_id)
    for lst in lists:
        tasks = get_tasks_in_list(lst["id"], debug=debug)
        all_tasks.extend(tasks)
    return all_tasks

def get_tasks_for_selected_sprint_label(folder_id, sprint_field_id, selected_sprint_name):
    """
    Returns tasks across the folder that are labeled with the selected sprint name.

    Args:
        folder_id (str): The ID of the folder being searched.
        sprint_field_id (str): Custom field ID for sprint label.
        selected_sprint_name (str): Human-readable sprint name.
    
    Returns:
        list: Tasks matching the selected sprint name.
    """
    matching_tasks = []
    all_tasks = get_all_tasks_from_folder_lists(folder_id)

    for task in all_tasks:
        sprint_labels = None
        for field in task.get("custom_fields", []):
            if field["id"] == sprint_field_id:
                sprint_labels = field.get("value")
                break

        if isinstance(sprint_labels, list):
            for label_id in sprint_labels:
                label_name = FIELD_ID_TO_SPRINT.get(label_id)
                if label_name == selected_sprint_name:
                    matching_tasks.append(task)
                    break
        elif sprint_labels:
            label_name = FIELD_ID_TO_SPRINT.get(sprint_labels)
            if label_name == selected_sprint_name:
                matching_tasks.append(task)

    return matching_tasks

def get_tasks_by_sprint_id_from_label_map(label_folder_id, task_folder_id, sprint_field_id, sprint_id):
    """
    Maps a sprint ID to a sprint name and returns all product tasks labeled with that sprint.
    
    Args:
        label_folder_id (str): The ID of the folder containing sprint lists.
        task_folder_id (str): The ID containing all the complete/closed tasks.
        sprint_field_id (str): Sprint label custom field ID.
        sprint_id (str): The ID of the selected sprint list.
    
    Returns:
        list: Tasks from the product folder labeled with the sprint.
    """
    sprint_lists = get_sprint_lists(label_folder_id)
    sprint_lookup = {s["id"]: s["name"] for s in sprint_lists}
    sprint_name = sprint_lookup.get(sprint_id)
    if not sprint_name:
        return []
    return get_tasks_for_selected_sprint_label(task_folder_id, sprint_field_id, sprint_name)

# ---------------------- OPTIONAL DEBUG HELPERS ----------------------

def extract_date_range(list_name):
    match = re.search(r"\((\d{1,2}/\d{1,2})\s*-\s*(\d{1,2}/\d{1,2})\)", list_name)
    if not match:
        return None, None
    year = datetime.today().year
    start = datetime.strptime(f"{match.group(1)}/{year}", "%m/%d/%Y")
    end = datetime.strptime(f"{match.group(2)}/{year}", "%m/%d/%Y")
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

def get_sprint_date_ranges(lists):
    ranges = {}
    for lst in lists:
        if "sprint" not in lst["name"].lower():
            continue
        start, end = extract_date_range(lst["name"])
        if start and end:
            ranges[lst["name"]] = (start, end)
    return ranges

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

# ---------------------- UNUSED BUT COULD BE USEFUL ----------------------

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


# ---------------------- MAIN EXECUTION ----------------------

if __name__ == "__main__":
    # 1. Get sprint lists and date ranges
    sprint_lists = get_sprint_lists(DEV_FOLDER_ID)
    sprint_ranges = {}

    for sprint in sprint_lists:
        name = sprint["name"]
        start, end = extract_date_range(name)
        if start and end:
            sprint_ranges[name] = (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    # 2. Get all tasks from all lists in the folder
    all_tasks = get_all_tasks_from_folder_lists(DEV_FOLDER_ID, debug=False)
    metadata = get_all_tasks_with_metadata(DEV_FOLDER_ID)
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

    # Let the user pick from all available sprints
    SPRINT_NAME_TO_LIST_ID = {lst["name"]: lst["id"] for lst in get_sprint_lists(DEV_FOLDER_ID)}
    print("Available Sprints:")
    for name in SPRINT_NAME_TO_LIST_ID:
        print(f" - {name}")

    selected_sprint = "Sprint 4 (6/4 - 6/17)"  # Replace with UI input
    tasks = get_tasks_for_selected_sprint_label(DEV_FOLDER_ID, CUSTOM_FIELD_ID, selected_sprint)

    print(f"\n📋 Tasks labeled with '{selected_sprint}':")
    for t in tasks:
        print(f" - {t['name']} (Task ID: {t['id']})")
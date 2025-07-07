import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import re
from collections import defaultdict

# Load API Token
load_dotenv()
token = os.getenv("CLICK_UP_TOKEN")

# ClickUp Identifiers
SPACE_ID = "90110749681"
FOLDER_ID = "90115096402"
FIELDSYNC_LIST_ID = "901110252032"
FS_WEB_APP_USER_FEEDBACK_ID = "901109641571"

HEADERS = {
    "Authorization": token,
    "accept": "application/json"
}

# ---------------------- API FUNCTIONS ----------------------

def get_lists_from_folder(folder_id):
    url = f"https://api.clickup.com/api/v2/folder/{folder_id}/list"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("lists", [])

def get_sprint_lists(folder_id):
    """Returns only lists that look like sprint folders."""
    all_lists = get_lists_from_folder(folder_id)
    return [lst for lst in all_lists if "sprint" in lst["name"].lower()]

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

def get_tasks_in_list(list_id):
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
    return tasks

def assign_to_sprint_by_close_date(task, sprint_ranges):
    for field in ["start_date", "date_closed", "date_done", "due_date", "date_updated"]:
        date_val = task.get(field)
        if date_val:
            try:
                close_dt = datetime.fromtimestamp(int(date_val) / 1000)
                break
            except:
                continue
    else:
        return None

    for sprint_name, (start_str, end_str) in sprint_ranges.items():
        start = datetime.strptime(start_str, "%Y-%m-%d")
        end = datetime.strptime(end_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        if start <= close_dt <= end:
            return sprint_name
    return None

def get_all_sprint_tasks(sprint_lists):
    seen_ids, sprint_map, task_to_sprints = set(), {}, {}
    for sprint in sprint_lists:
        name, id = sprint["name"], sprint["id"]
        tasks = get_tasks_in_list(id)
        closed = []
        for t in tasks:
            tid = t["id"]
            status = t.get("status", {}).get("status", "").lower()
            stype = t.get("status", {}).get("type", "").lower()
            if stype == "closed" or status in {"done", "complete", "closed"}:
                if tid not in seen_ids:
                    closed.append(t)
                    seen_ids.add(tid)
                task_to_sprints.setdefault(tid, []).append(name)
        sprint_map[name] = closed
    return sprint_map, task_to_sprints

def get_all_tasks_associated_with_sprints(folder_id):
    sprint_lists = get_sprint_lists(folder_id)
    sprint_ranges = get_sprint_date_ranges(sprint_lists)
    sprint_names = {s["name"] for s in sprint_lists if "fieldsync" not in s["name"].lower()}

    sprint_task_map, task_to_sprints = get_all_sprint_tasks(sprint_lists)
    fieldsync_tasks = get_tasks_in_list(FIELDSYNC_LIST_ID)

    backfilled = defaultdict(list)
    closed_labels = {"done", "complete", "closed", "released", "qa testing", "shipped"}

    for t in fieldsync_tasks:
        tid, status = t["id"], t.get("status", {})
        name, stype = status.get("status", "").lower(), status.get("type", "").lower()
        task_sprints = task_to_sprints.get(tid, [])
        real = [s for s in task_sprints if s in sprint_names]
        if (stype == "closed" or name in closed_labels) and (not real or (len(task_sprints) == 1 and "fieldsync" in task_sprints[0].lower())):
            assigned = assign_to_sprint_by_close_date(t, sprint_ranges)
            backfilled[assigned or "Unassigned"].append(t)

    sprint_closed = defaultdict(int)
    for s, tasks in sprint_task_map.items():
        for t in tasks:
            name = t.get("status", {}).get("status", "").lower()
            stype = t.get("status", {}).get("type", "").lower()
            if stype == "closed" or name in closed_labels:
                sprint_closed[s] += 1

    for s, tasks in backfilled.items():
        sprint_closed[s] += len(tasks)

    print("\n📊 Total Closed Tasks by Sprint:")
    for s in sorted(sprint_closed):
        print(f"- {s}: {sprint_closed[s]} closed tasks")

    # Combine and return final sprint task map
    all_sprint_tasks = defaultdict(list, sprint_task_map)
    for sprint, tasks in backfilled.items():
        all_sprint_tasks[sprint].extend(tasks)

    return all_sprint_tasks

def get_tasks_for_sprint_id(folder_id, sprint_id):
    sprint_lists = get_sprint_lists(folder_id)
    sprint_ranges = get_sprint_date_ranges(sprint_lists)
    sprint_names = {s["name"] for s in sprint_lists if "fieldsync" not in s["name"].lower()}
    sprint_lookup = {s["id"]: s["name"] for s in sprint_lists}

    target_sprint_name = sprint_lookup.get(sprint_id)
    if not target_sprint_name:
        return []

    # Get all sprint tasks (closed and mapped)
    sprint_task_map, task_to_sprints = get_all_sprint_tasks(sprint_lists)
    fieldsync_tasks = get_tasks_in_list(FIELDSYNC_LIST_ID)

    backfilled = defaultdict(list)
    closed_labels = {"done", "complete", "closed", "released", "qa testing", "shipped"}

    for t in fieldsync_tasks:
        tid, status = t["id"], t.get("status", {})
        name, stype = status.get("status", "").lower(), status.get("type", "").lower()
        task_sprints = task_to_sprints.get(tid, [])
        real = [s for s in task_sprints if s in sprint_names]
        if (stype == "closed" or name in closed_labels) and (not real or (len(task_sprints) == 1 and "fieldsync" in task_sprints[0].lower())):
            assigned = assign_to_sprint_by_close_date(t, sprint_ranges)
            if assigned == target_sprint_name:
                backfilled[assigned].append(t)

    # Combine main and backfilled tasks
    combined_tasks = sprint_task_map.get(target_sprint_name, []) + backfilled.get(target_sprint_name, [])
    return combined_tasks

def get_sprint_1_tasks():
    """Return manually assigned tasks for Sprint 1 by ClickUp task IDs."""

    sprint_1_task_ids = [
        "868dfpnjp",
        "868dfpnjb",
        "868dfpnk9",
        "868dfpmgu",
        "868d22e6r",
        "868dj2v1g",
        "868cu9f1w",
        "868dfpnk2",
        "868dgczbm",
        "868dfpmeh"  # <- "Allow null value" checkboxes
    ]

    # Pull from both FieldSync and Sprint 1 list to ensure we get everything
    fieldsync_tasks = get_tasks_in_list(FIELDSYNC_LIST_ID)
    sprint_1_list_tasks = get_tasks_in_list("901110337643")

    combined_tasks = {t["id"]: t for t in fieldsync_tasks + sprint_1_list_tasks}

    return [combined_tasks[tid] for tid in sprint_1_task_ids if tid in combined_tasks]

def get_sprint_2_tasks():
    """Return manually assigned tasks for Sprint 2 by ClickUp task IDs."""

    sprint_2_task_ids = [
        "868dfpmeh",
        "868dmy308",
        "868dgj0pg",
        "868dfpnjr",
        "868dfpmgn",
        "868dn73t5",
        "868cyeyy0",
        "868dfpnjh",
        "868drw8ud"
    ]

    # Pull from both FieldSync and Sprint 2 list to ensure we get everything
    fieldsync_tasks = get_tasks_in_list(FIELDSYNC_LIST_ID)
    user_feedback_tasks = get_tasks_in_list(FS_WEB_APP_USER_FEEDBACK_ID)
    sprint_2_list_tasks = get_tasks_in_list("901110499251")

    combined_tasks = {t["id"]: t for t in fieldsync_tasks + sprint_2_list_tasks + user_feedback_tasks}

    return [combined_tasks[tid] for tid in sprint_2_task_ids if tid in combined_tasks]

def get_sprint_3_tasks():
    """Return manually assigned tasks for Sprint 3 by ClickUp task IDs."""

    sprint_3_task_ids = [
        "868drynrb",
        "868dyc431",
        "868drgmn0",
        "868dxrp7x",
        "868dznu5z"
    ]

    # Pull from both FieldSync and Sprint 3 list to ensure we get everything
    fieldsync_tasks = get_tasks_in_list(FIELDSYNC_LIST_ID)
    sprint_3_list_tasks = get_tasks_in_list("901110682077")

    combined_tasks = {t["id"]: t for t in fieldsync_tasks + sprint_3_list_tasks}

    return [combined_tasks[tid] for tid in sprint_3_task_ids if tid in combined_tasks]

def get_sprint_4_tasks():
    """Return manually assigned tasks for Sprint 4 by ClickUp task IDs."""

    sprint_4_task_ids = [
        "868dfpmgd",
        "868e7uj2e",
        "868e7ukh1",
        "868cr2kqb",
        "868ecwwbd",
        "868ecx8gd",
        "868dzc2rj",
        "868dzawe8",
        "868dznu46",
        "868e7p66t",
        "868e7nff7",
        "868e7d6vr"
    ]

    # Pull from both FieldSync and Sprint 1 list to ensure we get everything
    fieldsync_tasks = get_tasks_in_list(FIELDSYNC_LIST_ID)
    sprint_4_list_tasks = get_tasks_in_list("901110912147")  # Sprint 1 list ID

    combined_tasks = {t["id"]: t for t in fieldsync_tasks + sprint_4_list_tasks}

    return [combined_tasks[tid] for tid in sprint_4_task_ids if tid in combined_tasks]

def get_sprint_5_tasks():
    """Return manually assigned tasks for Sprint 5 by ClickUp task IDs."""

    sprint_5_task_ids = [
        "868edehpe",
        "868e1auhc",
        "868eaxjpb",
        "868d23ht7",
        "868ef6tm3",
        "868efvah9",
        "868ee72xt",
        "868efta6g",
        "868ef7b9y"
    ]

    # Pull from both FieldSync and Sprint 1 list to ensure we get everything
    fieldsync_tasks = get_tasks_in_list(FIELDSYNC_LIST_ID)
    sprint_5_list_tasks = get_tasks_in_list("901111066665")  # Sprint 1 list ID

    combined_tasks = {t["id"]: t for t in fieldsync_tasks + sprint_5_list_tasks}

    return [combined_tasks[tid] for tid in sprint_5_task_ids if tid in combined_tasks]


# ---------------------- MAIN EXECUTION ----------------------

if __name__ == "__main__":
    # sprint_task_data = get_all_tasks_associated_with_sprints(FOLDER_ID)
    # print("\n📊 Total Closed Tasks by Sprint:")
    # for sprint, tasks in sorted(sprint_task_data.items()):
    #     print(f"- {sprint}: {len(tasks)} closed tasks")
    # sprint_1_tasks = get_sprint_1_tasks()
    # print("\n📋 Sprint 1 Tasks:")
    # for task in sprint_1_tasks:
    #     print(f"- {task['name']}")

    # sprint_2_tasks = get_sprint_2_tasks()
    # print("\n📋 Sprint 2 Tasks:")
    # for task in sprint_2_tasks:
    #     print(f"- {task['name']}")

    # sprint_3_tasks = get_sprint_3_tasks()
    # print("\n📋 Sprint 3 Tasks:")
    # for task in sprint_3_tasks:
    #     print(f"- {task['name']}")

    # sprint_4_tasks = get_sprint_4_tasks()
    # print("\n📋 Sprint 4 Tasks:")
    # for task in sprint_4_tasks:
    #     print(f"- {task['name']}")

    # sprint_5_tasks = get_sprint_5_tasks()
    # print("\n📋 Sprint 5 Tasks:")
    # for task in sprint_5_tasks:
    #     print(f"- {task['name']}")

    FOLDER_ID = "90115096402"
    TEST_SPRINT_ID = "901110499251"  # ← replace with actual Sprint 1–5 list ID from ClickUp

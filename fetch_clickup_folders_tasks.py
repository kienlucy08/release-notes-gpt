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
FOLDER_ID = "90115096402"
PRODUCT_FOLDER_ID = "90116436231"

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


SPACE_ID = "90110749681"
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

# def extract_date_range(list_name):
#     match = re.search(r"\((\d{1,2}/\d{1,2})\s*-\s*(\d{1,2}/\d{1,2})\)", list_name)
#     if not match:
#         return None, None
#     year = datetime.today().year
#     start = datetime.strptime(f"{match.group(1)}/{year}", "%m/%d/%Y")
#     end = datetime.strptime(f"{match.group(2)}/{year}", "%m/%d/%Y")
#     return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

# def get_sprint_date_ranges(lists):
#     ranges = {}
#     for lst in lists:
#         if "sprint" not in lst["name"].lower():
#             continue
#         start, end = extract_date_range(lst["name"])
#         if start and end:
#             ranges[lst["name"]] = (start, end)
#     return ranges

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

# def assign_to_sprint_by_close_date(task, sprint_ranges):
#     for field in ["start_date", "date_closed", "date_done", "due_date", "date_updated"]:
#         date_val = task.get(field)
#         if date_val:
#             try:
#                 close_dt = datetime.fromtimestamp(int(date_val) / 1000)
#                 break
#             except:
#                 continue
#     else:
#         return None

#     for sprint_name, (start_str, end_str) in sprint_ranges.items():
#         start = datetime.strptime(start_str, "%Y-%m-%d")
#         end = datetime.strptime(end_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
#         if start <= close_dt <= end:
#             return sprint_name
#     return None

# def get_all_sprint_tasks(sprint_lists):
#     seen_ids, sprint_map, task_to_sprints = set(), {}, {}
#     for sprint in sprint_lists:
#         name, id = sprint["name"], sprint["id"]
#         tasks = get_tasks_in_list(id)
#         closed = []
#         for t in tasks:
#             tid = t["id"]
#             status = t.get("status", {}).get("status", "").lower()
#             stype = t.get("status", {}).get("type", "").lower()
#             if stype == "closed" or status in {"done", "complete", "closed"}:
#                 if tid not in seen_ids:
#                     closed.append(t)
#                     seen_ids.add(tid)
#                 task_to_sprints.setdefault(tid, []).append(name)
#         sprint_map[name] = closed
#     return sprint_map, task_to_sprints

def get_all_tasks_from_folder_lists(folder_id, debug=False):
    """
    Fetches all tasks from all lists within a folder.
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

# def get_all_tasks_associated_with_sprints(folder_id):
#     sprint_lists = get_sprint_lists(folder_id)
#     sprint_ranges = get_sprint_date_ranges(sprint_lists)
#     sprint_names = {s["name"] for s in sprint_lists if "fieldsync" not in s["name"].lower()}

#     sprint_task_map, task_to_sprints = get_all_sprint_tasks(sprint_lists)
#     fieldsync_tasks = get_tasks_in_list(FIELDSYNC_LIST_ID)

#     backfilled = defaultdict(list)
#     closed_labels = {"done", "complete", "closed", "released", "qa testing", "shipped"}

#     for t in fieldsync_tasks:
#         tid, status = t["id"], t.get("status", {})
#         name, stype = status.get("status", "").lower(), status.get("type", "").lower()
#         task_sprints = task_to_sprints.get(tid, [])
#         real = [s for s in task_sprints if s in sprint_names]
#         if (stype == "closed" or name in closed_labels) and (not real or (len(task_sprints) == 1 and "fieldsync" in task_sprints[0].lower())):
#             assigned = assign_to_sprint_by_close_date(t, sprint_ranges)
#             backfilled[assigned or "Unassigned"].append(t)

#     sprint_closed = defaultdict(int)
#     for s, tasks in sprint_task_map.items():
#         for t in tasks:
#             name = t.get("status", {}).get("status", "").lower()
#             stype = t.get("status", {}).get("type", "").lower()
#             if stype == "closed" or name in closed_labels:
#                 sprint_closed[s] += 1

#     for s, tasks in backfilled.items():
#         sprint_closed[s] += len(tasks)

#     print("\n📊 Total Closed Tasks by Sprint:")
#     for s in sorted(sprint_closed):
#         print(f"- {s}: {sprint_closed[s]} closed tasks")

#     # Combine and return final sprint task map
#     all_sprint_tasks = defaultdict(list, sprint_task_map)
#     for sprint, tasks in backfilled.items():
#         all_sprint_tasks[sprint].extend(tasks)

#     return all_sprint_tasks

# def get_tasks_for_sprint_id(folder_id, sprint_id):
#     sprint_lists = get_sprint_lists(folder_id)
#     sprint_ranges = get_sprint_date_ranges(sprint_lists)
#     sprint_names = {s["name"] for s in sprint_lists if "fieldsync" not in s["name"].lower()}
#     sprint_lookup = {s["id"]: s["name"] for s in sprint_lists}

#     target_sprint_name = sprint_lookup.get(sprint_id)
#     if not target_sprint_name:
#         return []

#     # Get all sprint task mappings and backfilled tasks
#     sprint_task_map, task_to_sprints = get_all_sprint_tasks(sprint_lists)
#     fieldsync_tasks = get_tasks_in_list(FIELDSYNC_LIST_ID)
#     sprint_tasks_direct = get_tasks_in_list(sprint_id)  # pull tasks in sprint list directly

#     def get_subtasks(task):
#         return task.get("subtasks", [])

#     closed_labels = {"done", "complete", "closed", "qa testing", "deploy"}
#     backfilled = defaultdict(list)

#     for t in fieldsync_tasks:
#         tid = t["id"]
#         if tid in IGNORED_TASK_IDS:
#             continue

#         status = t.get("status", {})
#         name, stype = status.get("status", "").lower(), status.get("type", "").lower()
#         task_sprints = task_to_sprints.get(tid, [])
#         real = [s for s in task_sprints if s in sprint_names]

#         if (stype == "closed" or name in closed_labels) and (not real or (len(task_sprints) == 1 and "fieldsync" in task_sprints[0].lower())):
#             assigned = assign_to_sprint_by_close_date(t, sprint_ranges)
#             if assigned == target_sprint_name:
#                 backfilled[assigned].append(t)

#     # Combine: mapped sprint tasks + directly in sprint list + backfilled
#     mapped_tasks = sprint_task_map.get(target_sprint_name, [])
#     direct_tasks = sprint_tasks_direct

#     # Combine and deduplicate by task ID
#     combined = {t["id"]: t for t in mapped_tasks + direct_tasks + backfilled.get(target_sprint_name, []) if t["id"] not in IGNORED_TASK_IDS}

#     # Add subtasks
#     all_with_subtasks = list(combined.values())
#     for task in combined.values():
#         for subtask in get_subtasks(task):
#             if subtask["id"] not in IGNORED_TASK_IDS:
#                 all_with_subtasks.append(subtask)

#     return all_with_subtasks


# ---------------------- MAIN EXECUTION ----------------------

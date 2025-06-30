import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import re
import json

load_dotenv()
token = os.getenv("CLICK_UP_TOKEN")
SPACE_ID = "90110749681"
FOLDER_ID = "90115096402"

HEADERS = {
    "Authorization": token
}


def get_lists_from_folder(folder_id):
    url = f"https://api.clickup.com/api/v2/folder/{folder_id}/list"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("lists", [])


def extract_date_range(list_name):
    match = re.search(
        r"\((\d{1,2}/\d{1,2})\s*-\s*(\d{1,2}/\d{1,2})\)", list_name)
    if not match:
        return None, None
    year = datetime.today().year
    start = datetime.strptime(f"{match.group(1)}/{year}", "%m/%d/%Y")
    end = datetime.strptime(f"{match.group(2)}/{year}", "%m/%d/%Y")
    return start, end


def find_previous_sprint_list(lists):
    today = datetime.today()
    valid_sprints = []

    for lst in lists:
        start, end = extract_date_range(lst["name"])
        if start and end and end < today:
            valid_sprints.append((end, lst))

    # Sort by end date descending, pick the latest one that already ended
    if valid_sprints:
        valid_sprints.sort(reverse=True)
        return valid_sprints[0][1]
    return None


def find_current_sprint_list(lists):
    today = datetime.today()
    for lst in lists:
        start, end = extract_date_range(lst["name"])
        if start and end and start <= today <= end:
            return lst
    return None

def get_all_sprints(folder_id):
    lists = get_lists_from_folder(folder_id)
    # Filter only sprint-like lists (you can adjust logic if needed)
    sprints = [lst for lst in lists if "Sprint" in lst["name"]]
    return sorted(sprints, key=lambda x: x["name"], reverse=True)

def get_tasks_in_list(list_id):
    all_tasks = []
    page = 0
    while True:
        url = f"https://api.clickup.com/api/v2/list/{list_id}/task?page={page}&include_closed=true&subtasks=true"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        tasks = resp.json().get("tasks", [])
        all_tasks.extend(tasks)
        if not tasks or len(tasks) < 100:
            break
        page += 1

    print(f"📦 Retrieved {len(all_tasks)} total tasks from list {list_id}")
    for task in all_tasks:
        print(f"- {task['name']} (status: {task['status']['status']})")
    return all_tasks


def extract_full_task_data(task):
    priority = task.get("priority") or {}
    return {
        "id": task.get("id"),
        "name": task.get("name"),
        "description": task.get("description", ""),
        "status": task.get("status", {}).get("status"),
        "assignees": [
            assignee.get("username") or assignee.get("email")
            for assignee in task.get("assignees", [])
        ],
        "tags": [tag["name"] for tag in task.get("tags", [])],
        "start_date": task.get("start_date"),
        "due_date": task.get("due_date"),
        "priority": priority.get("priority"),
        "custom_fields": {
            field.get("name"): field.get("value")
            for field in task.get("custom_fields", [])
        },
        "url": f"https://app.clickup.com/t/{task.get('id')}",
    }



def get_done_statuses(list_id):
    url = f"https://api.clickup.com/api/v2/list/{list_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    statuses = resp.json().get("statuses", [])
    return [s["status"].lower() for s in statuses if s["type"] == "done"]


def filter_features_and_bugs(tasks):
    relevant = []
    for task in tasks:
        title = task["name"]
        desc = task.get("description", "")
        tags = [tag["name"].lower() for tag in task.get("tags", [])]
        if "bug" in tags or "feature" in tags:
            type_ = "Bug" if "bug" in tags else "Feature"
            relevant.append({
                "title": title,
                "desc": desc,
                "type": type_,
                "status": task.get("status", {}).get("status", "").lower()
            })
    return relevant

# if __name__ == "__main__":
#     print("🔍 Finding sprint...")

#     try:
#         sprint_lists = get_lists_from_folder(FOLDER_ID)
#         current_sprint = find_current_sprint_list(sprint_lists)

#         if not current_sprint:
#             print("⚠️ No sprint found based on today's date.")
#             exit(1)

#         print(f"📅 Current sprint: {current_sprint['name']}")
#         tasks = get_tasks_in_list(current_sprint["id"])
#         full_data = [extract_full_task_data(task) for task in tasks]
#         print(json.dumps(full_data, indent=2))
#         print(f"📦 Fetched {len(tasks)} tasks from list.")

#         complete_statuses = get_done_statuses(current_sprint["id"])
#         print(f"✅ Complete statuses: {complete_statuses}")

#         feature_bug_tasks = filter_features_and_bugs(tasks)
#         complete_items = [
#             f"{item['type']}: {item['title']}. {item['desc']}"
#             for item in feature_bug_tasks
#             if item["status"] in complete_statuses
#         ]

#         if not complete_items:
#             print("⚠️ No completed bugs or features found.")
#             exit(0)

#         print(f"📝 Found {len(complete_items)} completed bugs/features.")
#         # Call your generate_release_notes(complete_items) here if needed

#     except Exception as e:
#         print(f"❌ Error: {e}")
#         exit(1)

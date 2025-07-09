import os
from dotenv import load_dotenv

# Load from .env
load_dotenv()
CLICK_UP_TOKEN = os.getenv("CLICK_UP_TOKEN")

# Folder & Space IDs
DEV_FOLDER_ID = "90115096402"           
PRODUCT_FOLDER_ID = "90116436231"          
SPACE_ID = "90110749681"

# Optional Lists
FIELDSYNC_LIST_ID = "901110252032"
FS_WEB_APP_USER_FEEDBACK_ID = "901109641571"

# Saved notes base folder
NOTES_BASE_DIR = "static/saved_notes"

# Sprint label custom field
SPRINT_CUSTOM_FIELD_ID = "eaec1223-07ff-4ab6-bc9a-10dee0328b0d"

# Label ID → Sprint Name Mapping
FIELD_ID_TO_SPRINT = {
    "78caf6c8-6ebe-4475-8864-517fb2bc8287": "Sprint 6 (7/2 - 7/15)",
    "7c5de467-d7ab-4e4a-9b0b-544e083c04e2": "Sprint 5 (6/18 - 7/1)",
    "38fd6029-d934-4fc3-a06f-8f16eec12a51": "Sprint 3 (5/14 - 6/3)",
    "7ac74835-3f56-469d-bf88-3232ff36f03a": "Sprint 1 (4/16 - 4/29)",
    "ce584c56-7a9b-4210-ba0f-a495437d4a9a": "Sprint 2 (4/30 - 5/13)",
    "81702e1f-2913-4063-a546-1c27d7f5187c": "Sprint 4 (6/4 - 6/17)"
}

# Reusable headers
HEADERS = {
    "Authorization": CLICK_UP_TOKEN,
    "accept": "application/json"
}

# constants.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# --------------------------- CLICKUP CONSTANTS --------------------------

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
    "81702e1f-2913-4063-a546-1c27d7f5187c": "Sprint 4 (6/4 - 6/17)",
    "4155d35e-e3ec-4c45-8d58-2b2f28a477ef" : "Sprint 7 (7/16 - 7/29)",
    "3b8c2b64-18e2-4d1e-bf5e-e17abe4e4157" : "Sprint 8 (7/30 - 8/12)",
    "b6974cc8-aec9-45b2-b99f-5ab9e5db4017" : "Sprint 9 (8/13 - 8/26)",
    "af2ea55b-292d-4804-9df0-f4f946520c7f" : "Sprint 10 (8/27 - 9/9)",
    "6357fdfa-7114-49e7-9dcc-a9ea956936b0" : "Sprint 11 (9/10 - 9/23)",
    "97823526-f21c-440b-aee4-72ec7ebf4d15" : "Sprint 12 (9/24 - 10/7)",
    "bfe3503b-db1c-42cb-9e4f-1dc862855240" : "Sprint 13 (10/8 - 10/21)",
    "be7ac634-433c-405c-bed1-02a6b7faf19d" : "Sprint 14 (10/22 - 11/4)",
    "3d30a730-e8f8-43bf-bba7-59a1eb7a7f74" : "Sprint 15 (11/5 - 11/18)",
    "8893b2ff-46e0-4e4b-b830-c21c730b988c" : "Sprint 16 (11/19 - 12/2)",
    "588a0b88-85bd-4dd4-8b52-98631cf68b65" : "Sprint 17 (12/3 - 12/16)",
    "82251c75-e7cf-4467-a523-5b33275beab0" : "Sprint 18 (12/17 - 12/30)"
}
# Reusable headers
HEADERS = {
    "Authorization": CLICK_UP_TOKEN,
    "accept": "application/json"
}


# --------------------------- OPENAI CONSTANTS --------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLIENT = OpenAI(api_key=OPENAI_API_KEY)

# Constants for token usage
MAX_TOTAL_TOKENS = 4096
MAX_COMPLETION_TOKENS = 1500
MAX_INPUT_TOKENS = MAX_TOTAL_TOKENS - MAX_COMPLETION_TOKENS
TOKENS_PER_ITEM_EST = 100

# System prompt for GPT defining the formatting and tone of the release notes
SYSTEM_PROMPT = (
    "You are a helpful assistant that turns a list of developer-submitted bugs, features, and updates/enhancements"
    "into clear, structured release notes formatted in **rich text Markdown-style**. For each item, generate a clean summary with:\n"
    "• A bolded tag labeled with **Bug/Feature/Enhancement/Combination** based off of user selection for there type/tag\n"
    "• A bolded title (the name of the bug, feature, update, devops, or a combination of types e.g., feature & update)\n"
    "• Labels for Strategic Theme and Area of Impact seperated by | (these should be styled as tags)\n"
    "• A concise description in plain language\n"
    "• *Details:* section in italics, followed by a bullet list of found issues and or changes\n"
    "• *Impact to Users:* section in italics, followed by a bullet list of effects of the feature of bug fix on users\n"

    "Use **bullet points** and not slashes '-' for both details and user impact, and ensure output looks like a professional, formatted changelog. "
    "If a fix is too backend-focused, include it but add a note at the end: "
    "*This might be too complicated for a field tech to understand and isn’t necessary for the company release notes. However, it is important to acknowledge for software development updates.*\n\n"
    "Note that DevOps tasks will primarily only be used for backend software updates versus company wide updates. Include a note for DevOps specific tasks where they are exclusively for backend software team updates."

    "Strategic Theme definitions:\n"
    "- **Improve UX/UI** – Enhancements that improve user interface clarity, layout, workflows, or navigation. Typically involved in most web applicatio enhancements.\n"
    "- **System Hardening** – Fixes that improve reliability, performance, or technical integrity of the platform.\n"
    "- **Platform Expansion** – Support for new technologies, data types, or platform features.\n"
    "- **Business Development** – Customer management related, or enterprise tools. Usually not themes of the web application features and bugs.\n"
    "- **Field Enablement** – Anything that improves efficiency, visibility, or usability for field technicians specifically. Not to be confused with a field within the web application. This theme involves things that make it easier for field technicians to do their job.\n\n"

    "Here is an example update release note:\n"
    "**Granular Survey Tracker Performance Enhancement**  \n"
    "Improve UX/UI System Hardening | QC Editor Page, Survey Editing  \n"
    "Preformed a performance enhancement where users can now quickly review and tab through all fields without worry of fields being missed due to a performance issues with original feature\n"
    "*Details:*  \n"
    "• Fields were being reviewed quickly and the survey tracker didn't fully track all fields.\n"
    "• Fixed the performance issue which allows users to track fields no matter the review speed.\n"
    "*Impact to Users:*  \n"
    "• Users can now tab through fields quickly or slowly with no worry about fields going untracked\n"

    "Here is an example bug release note:\n"
    "**Flag Messages Assigned to the Wrong Surveys**  \n"
    "Improve UX/UI System Hardening | QC Editor Page, Survey Processing  \n"
    "Resolved a defect where flag messages entered in one survey were incorrectly shown in the next survey within the same Site Visit.\n"
    "*Details:*  \n"
    "• Flags added to Compound surveys were mistakenly shown in Structure surveys.\n"
    "• Fixed incorrect data linkage causing the issue.\n"
    "*Impact to Users:*  \n"
    "• Flags now remain in their original survey context.\n"
    "• Prevents confusion during review and processing.\n"

    "Here is an example feature release note:\n"
    "**Site Id Column Added to Site Visits Dashboard Tab**  \n"
    "Improve UX/UI | Dashboard Tables  \n"
    "Introduced a new column for Site ID (SiteIdentifier) in the Site Visits dashboard tab, improving visibility and searchability for key location identifiers.\n"
    "*Details:*  \n"
    "• Added SiteIdentifier as a dedicated column in the Site Visits table.\n"
    "• Enabled full support for filtering and sorting on this column.\n"
    "• Ensures alignment with other tables where Site ID is a core reference field.\n"
    "*Impact to Users:*  \n"
    "• Users can now quickly locate and differentiate Site Visits based on Site ID.\n"
    "• Improves dashboard consistency and reduces the need to cross-reference external datasets for identifiers.\n"
    "• Streamlines workflows for users managing multiple site-level records.\n"

    "Here is the list of completed items:"
)
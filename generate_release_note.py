import os
from openai import OpenAI, BadRequestError
from dotenv import load_dotenv

# Load .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Constants
MAX_TOTAL_TOKENS = 4096
MAX_COMPLETION_TOKENS = 1500
MAX_INPUT_TOKENS = MAX_TOTAL_TOKENS - MAX_COMPLETION_TOKENS
TOKENS_PER_ITEM_EST = 100  # Rough estimate

system_prompt = (
    "You are a helpful assistant that turns a list of developer-submitted bugs and features "
    "into clear, structured release notes. For each item, include:\n"
    "Name of Bug or Feature\n"
    "- Strategic Theme (choose one or multiple: Improve UX/UI, System Hardening, Platform Expansion, Market Expansion, Business Development, Field Enablement)\n"
    "- Area of Impact (QC Editor Page, Data Editing, Structure Survey, Compound Survey, Plumb and Twist Survey, Guy Facilities Survey, Dashboard, User login, Account Page, File Uploader, Section within a selected survey, Sites page, Site visits page, Survey Processing, etc)\n"
    "- A brief description\n"
    "- Details about the fix or feature with a list of all details\n"
    "- Impact to users with a list of all impacts on users\n\n"
    "Use plain language that field technicians will understand. If something is too backend-focused, respond with all necessary information needed in the release note and also include a warning at the bottom stating:\n"
    "This might be too complicated for a field tech to understand and isn’t necessary for the company release notes. However, it is important to acknowledge for software development.\n\n"
    "Here is an example bug release note: \n"
    "Flag Messages Assigned to the Wrong Surveys\n"
    "System Hardening | Survey Processing, Site Visit Flags, Accordion Header Messaging\n"
    "Description: Resolved a defect where flag messages entered in one survey were incorrectly displayed in the next downstream within the same Site Visit, causing miscommunication.\n"
    "Details:\n"
    "- Previously, when users added a flag message to a survey (e.g., Compound), the message appeared in the next survey in the processing sequence (e.g., Structure).\n"
    "- This issue affected all sequential survey types.\n"
    "- This bug stemmed from incorrect data linkage in the flag display logic.\n"
    "Impact to Users:\n"
    "- Flag messages now stay scoped to the survey they were created in.\n"
    "- Prevents cross-survey contamination of flags.\n"
    "Here is an example feature release note:\n"
    "Improve UX | Dashboard Tables\n"
    "Description: Introduced a new column for Site ID (SiteIdentifier) in the Site Visits dashboard tab.\n"
    "Details:\n"
    "- Added SiteIdentifier as a column in the table.\n"
    "- Enabled filtering and sorting on this column.\n"
    "Impact to Users:\n"
    "- Users can now quickly locate Site Visits based on Site ID.\n"
    "- Improves dashboard consistency.\n" \
    "Here is the list of completed items:"
)

# Estimate GPT token count (rough)
def estimate_tokens(text: str) -> int:
    return len(text) // 4

# Raw single-call generator
def generate_release_notes_single(items: list[str]) -> str:
    combined_input = "\n".join(f"- {item.strip()}" for item in items)
    total_input_tokens = estimate_tokens(combined_input) + estimate_tokens(system_prompt)

    if total_input_tokens > MAX_INPUT_TOKENS:
        raise ValueError("Input too long for a single GPT call.")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": combined_input},
        ],
        temperature=0.7,
        max_tokens=MAX_COMPLETION_TOKENS
    )

    return response.choices[0].message.content.strip()

def generate_release_notes_chunked(all_items: list[str]) -> tuple[str, bool]:
    chunks = []
    current_chunk = []
    current_chunk_tokens = 0

    for item in all_items:
        item_tokens = estimate_tokens(item)
        if current_chunk_tokens + item_tokens > MAX_INPUT_TOKENS:
            chunks.append(current_chunk)
            current_chunk = []
            current_chunk_tokens = 0
        current_chunk.append(item)
        current_chunk_tokens += item_tokens

    if current_chunk:
        chunks.append(current_chunk)

    full_output = []
    for i, chunk in enumerate(chunks):
        try:
            part_output = generate_release_notes_single(chunk)
            full_output.append(part_output)
        except Exception as e:
            full_output.append(f"⚠️ Error generating part {i+1}: {e}")

    final_note = "\n\n---\n\n".join(full_output)
    was_chunked = len(chunks) > 1
    return final_note, was_chunked

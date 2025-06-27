import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

system_prompt = (
    "You are a helpful assistant that turns a list of developer-submitted bugs and features "
    "into clear, structured release notes. For each item, include:\n"
    "Name of Bug or Feature\n"
    "- Strategic Theme (choose one or multiple: Improve UX/UI, System Hardening, Platform Expansion, Market Expansion, Business Development, Field Enablement)\n"
    "- Area of Impact (QC Editor Page, Data Editing, Structure Survey, Compound Survey, Plumb and Twist Survey, Guy Facilities Survey, Dashboard, User login, Account Page, File Uploader, Section within a selected survey, Sites page, Site visits page, Survey Processing, etc) You can pick and choose which areas seem to have the biggest area of impact.\n"
    "- A brief description\n"
    "- Details about the fix or feature with a list of all details\n"
    "- Impact to users with a list of all impacts on users\n\n"
    "Use plain language that field technicians will understand. If something is too backend-focused, just respond with:\n"
    "'This might be too complicated for a field tech to understand and isn’t necessary for the release notes.'\n\n" \
    "Here is an example bug release note: \n"
    "Flag Messages Assigned to the Wrong Surveys"
    "System Hardening | Survey Processing, Site Visit Flags, Accordion Header Messaging \n"
    "Description: Resolved a defect where flag messages entered in one survey were incorrectly displayed in the next downstream within the same Site Visit, causing miscommunication across grouped surveys. \n"
    "Details:\n" 
    "- Previously, when users added a flag message to a survey (e.g., Compound), the message appeared in the next survey in the processing sequence (e.g., Structure).\n"
    "- This issue affected all sequential survey types (Compound → Structure → Guy Facilities → P & T), causing a circular shift in flag display order. \n"
    "- This bug stemmed from incorrect data linkage in the flag display logic, which pulled flag data from the wrong survey GUID. \n"
    "Impact to Users:\n"
    "- Flag messages now stay scoped to the survey they were created in , ensuring that QA notes and field flags are only visible in their intended context.\n"
    "- Prevents cross-survey contamination of flags, reducing the risk of confusion during review, reporting, or reprocessing. \n"
    "Here is an example feature release note: \n"
    "Improve UX | Dashboard Tables\n"
    "Description: Introduced a new column for Site ID (SiteIdentifier) in the Site Visits dashboard tab, improving visibility and searchability for key location identifiers.\n"
    "Details:\n"
    "- Added SiteIdentifier as a dedicated column in the Site Visits table.\n"
    "- Enabled full support for filtering and sorting on this column.\n"
    "- Ensures alignment with other tables where Site ID is a core reference field.\n"
    "Impact to Users:\n"
    "- Users can now quickly locate and differentiate Site Visits based on Site ID.\n"
    "- Improves dashboard consistency and reduces the need to cross-reference external datasets for identifiers.\n"
    "- Streamlines workflows for users managing multiple site-level records.\n"
    "Here is the list of completed items:"
)

def generate_release_notes(all_items: list[str]) -> str:
    estimated_tokens_per_item = 500
    buffer_tokens = 200
    max_tokens = estimated_tokens_per_item * len(all_items) + buffer_tokens

    combined_input = "\n".join(f"- {item.strip()}" for item in all_items)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": combined_input},
        ],
        temperature=0.7,
        max_tokens=max_tokens  # Adjust based on number of items
    )

    return response.choices[0].message.content.strip()

# Example usage
if __name__ == "__main__":
    print("📝 Interactive Release Notes Entry")
    print("Type 'bug' or 'feature' to begin entering an item.")
    print("Type 'done' to finish and generate release notes.")
    print("Press Enter on a blank line to finish each item.\n")

    entries = []

    while True:
        item_type = input("What type is this? (bug/feature/done): ").strip().lower()
        if item_type == "done":
            break
        if item_type not in ["bug", "feature"]:
            print("❌ Invalid input. Please enter 'bug', 'feature', or 'done'.")
            continue

        print(f"Enter the description for this {item_type}.")
        print("Press Enter on a blank line to submit it.\n")

        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line.strip())

        if lines:
            entry = f"{item_type.capitalize()}: " + " ".join(lines)
            entries.append(entry)
            print("✅ Entry added.\n")
        else:
            print("⚠️ No description entered. Skipping.\n")

    if entries:
        print("🧠 Generating release notes...\n")
        result = generate_release_notes(entries)
        print("\n📦 Final Release Notes:\n")
        print(result)
    else:
        print("⚠️ No entries submitted.")



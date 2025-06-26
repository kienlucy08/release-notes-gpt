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
    "Name of Bug or Feature"
    "- Strategic Theme (choose one or multiple: Improve UX/UI, System Hardening, Platform Expansion, Market Expansion, Business Development, Field Enablement)\n"
    "- Area of Impact (QC Editor Page, Data Editing, Structure Survey, Compound Survey, Plumb and Twist Survey, Guy Facilities Survey, Dashboard, User login, Account Page, File Uploader, Section within a selected survey, Sites page, Site visits page, Survey Processing, etc) You can pick and choose which areas seem to have the biggest area of impact.\n"
    "- Description\n"
    "- Details about the fix or feature\n"
    "- Impact to users\n\n"
    "Use plain language that field technicians will understand. If something is too backend-focused, just respond with:\n"
    "'This might be too complicated for a field tech to understand and isn’t necessary for the release notes.'\n\n"
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
    print("Paste in your bugs and features (one per line). Blank line to finish:")
    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)

    if lines:
        result = generate_release_notes(lines)
        print("\nRelease Notes:\n")
        print(result)
    else:
        print("No input provided.")

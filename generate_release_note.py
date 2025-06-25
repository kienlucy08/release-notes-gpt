import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def generate_release_note(input_text: str) -> str:
    system_prompt = (
        "You are a helpful assistant that turns developer-submitted bugs and feature summaries into clear, structured release notes. "
        "Each release note should include the following elements: strategic theme, area of impact, description, details about the fix or feature, and the impact to users. "
        "These notes are specifically for a Web Application used by field technicians who inspect towers and generate reports, as well as QC technicians who review their work. "
        "Most changes focus on improving this application for those users. "
        "Use a tone that field technicians can easily understand. If a change is too technical or backend-focused (e.g., infrastructure, architecture, etc.), respond with: "
        "\"This might be too complicated for a field tech to understand and isn’t necessary for the release notes.\" "
        "Focus on communicating visual updates and bug fixes that directly affect end users. Backend-only tasks can generally be skipped in the notes. "
        "For bugs, you’ll receive a brief description and steps to reproduce. For features, you’ll receive a summary and the required outcomes. "
        "All items you receive are considered completed — your job is to frame them into concise, helpful release notes. "
        "Use one of the following strategic themes for each note: Improve UX/UI, System Hardening, Platform Expansion, Market Expansion, Business Development, or Field Enablement. "
        "The most common themes are Improve UX/UI and System Hardening."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate a release note for: {input_text}"},
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    user_input = input("Describe the bug or feature: ")
    note = generate_release_note(user_input)
    print("\n📝 Release Note:\n" + note)

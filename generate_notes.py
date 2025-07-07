import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Constants for token usage
MAX_TOTAL_TOKENS = 4096
MAX_COMPLETION_TOKENS = 1500
MAX_INPUT_TOKENS = MAX_TOTAL_TOKENS - MAX_COMPLETION_TOKENS
TOKENS_PER_ITEM_EST = 100

# System prompt for GPT defining the formatting and tone of the release notes
system_prompt = (
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

def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a given string.

    Args:
        text (str): The text to estimate token count for.

    Returns:
        int: Estimated number of tokens based on average of 4 characters per token.
    """
    return len(text) // 4

def generate_release_notes_single(items: list[str]) -> str:
    """
    Generate a release note summary for a list of items using OpenAI in a single request

    Args:
        items (list[str]): List of developer-submitted items (bugs, features, etc)

    Returns:
        str: A formatted markdown-stlye release note response from GPT
    
    Raises:
        ValueError: If total estimated input tokens exceed model limit
    """
    # combine user entrties into a single string input
    combined_input = "\n".join(f"- {item.strip()}" for item in items)

    # estimate total tokens to prevent a model overload
    total_input_tokens = estimate_tokens(
        combined_input) + estimate_tokens(system_prompt)
    if total_input_tokens > MAX_INPUT_TOKENS:
        raise ValueError("Input too long for a single OpenAI call.")

    # Send a request to OpenAI GPT
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
    """
    Generate release notes by breaking large item lists into smaller chunks
    that fit within token limits, and calling OpenAI for each chunk.
    
    Args:
        all_items (list[str]): List of all developer-submitted items/tickets
    
    Returns:
        tuple[str, bool]: A tuple containing:
            - Combined release note string from all chunks.
            - A boolean indicating wheather chunking was required
    """
    def split_large_chunk(chunk):
        """
        Splits a chunk into two halves.

        Args:
            chunk (list[str]): The chunk to split.

        Returns:
            list[list[str]]: Two smaller chunks.
        """
        mid = len(chunk) // 2
        return [chunk[:mid], chunk[mid:]]

    # Group entries into chunks that fit within the input token limit
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
    original_chunk_count = len(chunks)
    i = 0

    while i < len(chunks):
        chunk = chunks[i]
        try:
            # Try to generate notes for the current chunk
            part_output = generate_release_notes_single(chunk)
            full_output.append(part_output)
            # move to next chunk
            i += 1 
        except ValueError as e:
            # If even the chunk is too large, split further
            if len(chunk) <= 1:
                full_output.append(f"⚠️ Error generating part {i+1}: {e}")
                # still move to next
                i += 1 
            else:
                subchunks = split_large_chunk(chunk)
                # replace current chunk with its split
                chunks[i:i+1] = subchunks  
                # signal chunking occurred
                original_chunk_count = max(original_chunk_count, len(chunks))

    final_note = "\n\n---\n\n".join(full_output)
    was_chunked = original_chunk_count > 1
    return final_note, was_chunked

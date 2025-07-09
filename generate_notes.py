from constants import (CLIENT,
                       MAX_COMPLETION_TOKENS,
                       MAX_INPUT_TOKENS,
                       SYSTEM_PROMPT)

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
        combined_input) + estimate_tokens(SYSTEM_PROMPT)
    if total_input_tokens > MAX_INPUT_TOKENS:
        raise ValueError("Input too long for a single OpenAI call.")

    # Send a request to OpenAI GPT
    response = CLIENT.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
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
                full_output.append(f"Error generating part {i+1}: {e}")
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

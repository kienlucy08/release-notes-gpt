const Anthropic = require('@anthropic-ai/sdk');
const { SYSTEM_PROMPT, MAX_COMPLETION_TOKENS, MAX_INPUT_TOKENS } = require('../config/constants');

const client = new Anthropic();

function estimateTokens(text) {
  return Math.floor(text.length / 4);
}

async function generateReleaseNotesSingle(items) {
  const combinedInput = items.map((item) => `- ${item.trim()}`).join('\n');

  const totalInputTokens = estimateTokens(combinedInput) + estimateTokens(SYSTEM_PROMPT);
  if (totalInputTokens > MAX_INPUT_TOKENS) {
    throw new Error('Input too long for a single API call.');
  }

  const message = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: MAX_COMPLETION_TOKENS,
    system: SYSTEM_PROMPT,
    messages: [{ role: 'user', content: combinedInput }],
    temperature: 0.7,
  });

  return message.content[0].text.trim();
}

async function generateReleaseNotesChunked(allItems) {
  function splitLargeChunk(chunk) {
    const mid = Math.floor(chunk.length / 2);
    return [chunk.slice(0, mid), chunk.slice(mid)];
  }

  const chunks = [];
  let currentChunk = [];
  let currentChunkTokens = 0;

  for (const item of allItems) {
    const itemTokens = estimateTokens(item);
    if (currentChunkTokens + itemTokens > MAX_INPUT_TOKENS) {
      chunks.push(currentChunk);
      currentChunk = [];
      currentChunkTokens = 0;
    }
    currentChunk.push(item);
    currentChunkTokens += itemTokens;
  }

  if (currentChunk.length > 0) {
    chunks.push(currentChunk);
  }

  const fullOutput = [];
  let originalChunkCount = chunks.length;
  let i = 0;

  while (i < chunks.length) {
    const chunk = chunks[i];
    try {
      const partOutput = await generateReleaseNotesSingle(chunk);
      fullOutput.push(partOutput);
      i++;
    } catch (err) {
      if (chunk.length <= 1) {
        fullOutput.push(`Error generating part ${i + 1}: ${err.message}`);
        i++;
      } else {
        const subchunks = splitLargeChunk(chunk);
        chunks.splice(i, 1, ...subchunks);
        originalChunkCount = Math.max(originalChunkCount, chunks.length);
      }
    }
  }

  const finalNote = fullOutput.join('\n\n---\n\n');
  const wasChunked = originalChunkCount > 1;
  return { notes: finalNote, wasChunked };
}

module.exports = {
  generateReleaseNotesSingle,
  generateReleaseNotesChunked,
};

const express = require('express');
const router = express.Router();
const { generateReleaseNotesChunked } = require('../services/anthropic');

// POST /api/generate - Generate release notes from entries
router.post('/generate', async (req, res) => {
  const { entries, sprintName } = req.body;

  if (!entries || !entries.length || !sprintName) {
    return res.status(400).json({ error: 'entries and sprintName are required' });
  }

  try {
    const { notes, wasChunked } = await generateReleaseNotesChunked(entries);
    res.json({ notes, wasChunked });
  } catch (err) {
    console.error('Error generating release notes:', err);
    res.status(500).json({ error: 'Failed to generate release notes' });
  }
});

module.exports = router;

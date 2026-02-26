const express = require('express');
const router = express.Router();
const { getSprintLists, getTasksBySprintIdFromLabelMap } = require('../services/clickup');
const { DEV_FOLDER_ID, PRODUCT_FOLDER_ID, SPRINT_CUSTOM_FIELD_ID } = require('../config/constants');

// GET /api/sprints - Returns sprint list from ClickUp
router.get('/sprints', async (req, res) => {
  try {
    const allLists = await getSprintLists(DEV_FOLDER_ID);
    const sprints = allLists
      .filter((lst) => lst.name.includes('Sprint'))
      .map((lst) => ({ id: lst.id, name: lst.name }));
    res.json(sprints);
  } catch (err) {
    console.error('Error fetching sprints:', err);
    res.status(500).json({ error: 'Failed to fetch sprints from ClickUp' });
  }
});

// GET /api/tasks?sprint_id=X - Returns tasks for a sprint with tags and descriptions
router.get('/tasks', async (req, res) => {
  const { sprint_id } = req.query;
  if (!sprint_id) return res.json([]);

  try {
    const tasks = await getTasksBySprintIdFromLabelMap(
      DEV_FOLDER_ID,
      PRODUCT_FOLDER_ID,
      SPRINT_CUSTOM_FIELD_ID,
      sprint_id
    );
    const result = tasks.map((t) => ({
      id: t.id,
      name: t.name,
      tags: t.tags || [],
      description: t.description || '',
    }));
    res.json(result);
  } catch (err) {
    console.error('Error fetching tasks:', err);
    res.status(500).json({ error: 'Failed to fetch tasks from ClickUp' });
  }
});

module.exports = router;

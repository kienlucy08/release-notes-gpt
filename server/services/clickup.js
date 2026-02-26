const { HEADERS, FIELD_ID_TO_SPRINT } = require('../config/constants');

async function getListsFromFolder(folderId) {
  const url = `https://api.clickup.com/api/v2/folder/${folderId}/list`;
  const resp = await fetch(url, { headers: HEADERS });
  if (!resp.ok) throw new Error(`ClickUp API error: ${resp.status}`);
  const data = await resp.json();
  return data.lists || [];
}

async function getSprintLists(folderId) {
  const allLists = await getListsFromFolder(folderId);
  return allLists.filter((lst) => lst.name.toLowerCase().includes('sprint'));
}

async function getTasksInList(listId, includeSubtasks = true) {
  const tasks = [];
  let page = 0;
  while (true) {
    const url = `https://api.clickup.com/api/v2/list/${listId}/task?page=${page}&limit=100&include_closed=true`;
    const resp = await fetch(url, { headers: HEADERS });
    if (!resp.ok) throw new Error(`ClickUp API error: ${resp.status}`);
    const data = await resp.json();
    let chunk = data.tasks || [];
    if (!includeSubtasks) {
      chunk = chunk.filter((task) => !task.parent);
    }
    tasks.push(...chunk);
    if (chunk.length < 100) break;
    page++;
  }
  return tasks;
}

async function getAllTasksFromFolderLists(folderId) {
  const allTasks = [];
  const lists = await getListsFromFolder(folderId);
  for (const lst of lists) {
    const tasks = await getTasksInList(lst.id, true);
    allTasks.push(...tasks);
  }
  return allTasks;
}

async function getTasksForSelectedSprintLabel(folderId, sprintFieldId, selectedSprintName) {
  const matchingTasks = [];
  const allTasks = await getAllTasksFromFolderLists(folderId);

  for (const task of allTasks) {
    let sprintLabels = null;
    for (const field of task.custom_fields || []) {
      if (field.id === sprintFieldId) {
        sprintLabels = field.value;
        break;
      }
    }

    if (Array.isArray(sprintLabels)) {
      for (const labelId of sprintLabels) {
        const labelName = FIELD_ID_TO_SPRINT[labelId];
        if (labelName === selectedSprintName) {
          matchingTasks.push(task);
          break;
        }
      }
    } else if (sprintLabels) {
      const labelName = FIELD_ID_TO_SPRINT[sprintLabels];
      if (labelName === selectedSprintName) {
        matchingTasks.push(task);
      }
    }
  }

  return matchingTasks;
}

async function getTasksBySprintIdFromLabelMap(labelFolderId, taskFolderId, sprintFieldId, sprintId) {
  const sprintLists = await getSprintLists(labelFolderId);
  const sprintLookup = {};
  for (const s of sprintLists) {
    sprintLookup[s.id] = s.name;
  }
  const sprintName = sprintLookup[sprintId];
  if (!sprintName) return [];
  return getTasksForSelectedSprintLabel(taskFolderId, sprintFieldId, sprintName);
}

module.exports = {
  getListsFromFolder,
  getSprintLists,
  getTasksInList,
  getAllTasksFromFolderLists,
  getTasksForSelectedSprintLabel,
  getTasksBySprintIdFromLabelMap,
};

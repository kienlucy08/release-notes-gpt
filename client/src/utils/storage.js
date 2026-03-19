const STORAGE_KEY = 'releaseNotes';

function loadStore() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : { sprintFolders: {} };
  } catch {
    return { sprintFolders: {} };
  }
}

function persistStore(store) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch (err) {
    console.error('Failed to save to localStorage:', err);
  }
}

export function loadAllNotes() {
  const store = loadStore();
  return Object.entries(store.sprintFolders).map(([folderId, data]) => ({
    name: data.name,
    folder: folderId,
    files: Object.keys(data.notes).sort().reverse(),
  }));
}

export function saveNote(sprintName, sprintFolderId, filename, content) {
  const store = loadStore();
  if (!store.sprintFolders[sprintFolderId]) {
    store.sprintFolders[sprintFolderId] = { name: sprintName, notes: {} };
  }
  store.sprintFolders[sprintFolderId].notes[filename] = {
    content,
    createdAt: new Date().toISOString(),
  };
  persistStore(store);
}

export function getNoteContent(folderId, filename) {
  const store = loadStore();
  return store.sprintFolders[folderId]?.notes[filename]?.content || null;
}

export function deleteSingleNote(folderId, filename) {
  const store = loadStore();
  if (store.sprintFolders[folderId]?.notes[filename]) {
    delete store.sprintFolders[folderId].notes[filename];
    if (Object.keys(store.sprintFolders[folderId].notes).length === 0) {
      delete store.sprintFolders[folderId];
    }
    persistStore(store);
  }
}

export function deleteAllNotes(folderId) {
  const store = loadStore();
  delete store.sprintFolders[folderId];
  persistStore(store);
}

export function renameNote(folderId, oldName, newName) {
  const store = loadStore();
  const folder = store.sprintFolders[folderId];
  if (folder?.notes[oldName]) {
    folder.notes[newName] = folder.notes[oldName];
    delete folder.notes[oldName];
    persistStore(store);
  }
}

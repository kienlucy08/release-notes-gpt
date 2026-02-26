import { useState, useEffect, useCallback } from 'react';
import { get, post } from './api/apiClient';
import { loadAllNotes, saveNote } from './utils/storage';
import SprintSelector from './components/SprintSelector';
import EntryModeToggle from './components/EntryModeToggle';
import ManualEntryForm from './components/ManualEntryForm';
import AutoTaskSelect from './components/AutoTaskSelect';
import FileNameInput from './components/FileNameInput';
import GenerateButton from './components/GenerateButton';
import CurrentItems from './components/CurrentItems';
import GeneratedNotes from './components/GeneratedNotes';
import PastSprintNotes from './components/PastSprintNotes';

function App() {
  // Sprint data
  const [sprints, setSprints] = useState([]);
  const [selectedSprint, setSelectedSprint] = useState('');

  // Entry mode
  const [entryMode, setEntryMode] = useState('manual');

  // Manual mode entries
  const [manualEntries, setManualEntries] = useState([{ tag: 'Feature', description: '' }]);

  // Auto mode state
  const [autoTasks, setAutoTasks] = useState([]);
  const [selectedTaskIds, setSelectedTaskIds] = useState(new Set());
  const [extraEntries, setExtraEntries] = useState([{ tag: 'Feature', description: '' }]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);

  // File name
  const [customFilename, setCustomFilename] = useState('');

  // Generation state
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedNotes, setGeneratedNotes] = useState(null);
  const [wasChunked, setWasChunked] = useState(false);
  const [submittedEntries, setSubmittedEntries] = useState([]);
  const [savedFilename, setSavedFilename] = useState(null);
  const [error, setError] = useState(null);

  // Saved notes
  const [savedNotes, setSavedNotes] = useState(() => loadAllNotes());

  // Load sprints on mount
  useEffect(() => {
    get('/sprints')
      .then(setSprints)
      .catch((err) => console.error('Failed to load sprints:', err));
  }, []);

  // Load tasks when sprint changes in auto mode
  const loadTasks = useCallback(async (sprintId) => {
    if (!sprintId) return;
    setIsLoadingTasks(true);
    try {
      const tasks = await get(`/tasks?sprint_id=${sprintId}`);
      setAutoTasks(tasks);
      setSelectedTaskIds(new Set(tasks.map((t) => t.id)));
    } catch (err) {
      console.error('Failed to load tasks:', err);
      setAutoTasks([]);
    } finally {
      setIsLoadingTasks(false);
    }
  }, []);

  function handleSprintChange(sprintId) {
    setSelectedSprint(sprintId);
    if (entryMode === 'auto' && sprintId) {
      loadTasks(sprintId);
    }
  }

  function handleEntryModeChange(mode) {
    setEntryMode(mode);
    if (mode === 'auto' && selectedSprint) {
      loadTasks(selectedSprint);
    }
  }

  function handleToggleTask(taskId, checked) {
    setSelectedTaskIds((prev) => {
      const next = new Set(prev);
      if (checked) {
        next.add(taskId);
      } else {
        next.delete(taskId);
      }
      return next;
    });
  }

  async function handleGenerate() {
    setError(null);

    if (!selectedSprint) {
      setError('Please select a sprint.');
      return;
    }

    let entries = [];

    if (entryMode === 'auto') {
      const chosenTasks = autoTasks.filter((t) => selectedTaskIds.has(t.id));
      entries = chosenTasks.map((task) => {
        const tags = (task.tags || []).map((t) => (t.name || '').toLowerCase());
        let tag = 'Feature';
        if (tags.includes('bug')) tag = 'Bug';
        else if (tags.includes('devops')) tag = 'DevOps';
        else if (tags.includes('enhancement')) tag = 'Enhancement';
        else if (tags.includes('feature')) tag = 'Feature';
        return `${tag}: ${task.name.trim()}\n${(task.description || '').trim()}:`;
      });
      // Append extra manual entries
      entries.push(
        ...extraEntries
          .filter((e) => e.description.trim())
          .map((e) => `${e.tag}: ${e.description.trim()}`)
      );
    } else {
      entries = manualEntries
        .filter((e) => e.description.trim())
        .map((e) => `${e.tag}: ${e.description.trim()}`);
    }

    if (entries.length === 0) {
      setError('Please add at least one entry.');
      return;
    }

    setIsGenerating(true);
    setSubmittedEntries(entries);

    try {
      const sprintName = sprints.find((s) => s.id === selectedSprint)?.name || selectedSprint;
      const result = await post('/generate', { entries, sprintName });

      setGeneratedNotes(result.notes);
      setWasChunked(result.wasChunked);

      // Auto-save to localStorage
      const filename = customFilename.trim()
        ? customFilename.trim().replace(/[^a-zA-Z0-9_-]/g, '') + '.txt'
        : `release_notes_${new Date().toISOString().slice(0, 19).replace(/[:-]/g, '').replace('T', '_')}.txt`;

      saveNote(sprintName, selectedSprint, filename, result.notes);
      setSavedFilename(filename);
      setSavedNotes(loadAllNotes());
    } catch (err) {
      setError(`Generation failed: ${err.message}`);
    } finally {
      setIsGenerating(false);
    }
  }

  function handleStartOver() {
    setGeneratedNotes(null);
    setWasChunked(false);
    setSubmittedEntries([]);
    setManualEntries([{ tag: 'Feature', description: '' }]);
    setExtraEntries([{ tag: 'Feature', description: '' }]);
    setSavedFilename(null);
    setCustomFilename('');
    setError(null);
  }

  function handleNotesChanged() {
    setSavedNotes(loadAllNotes());
  }

  return (
    <div className="container">
      <h1 className="custom-title">FieldSync Release Notes Generator</h1>

      {!generatedNotes && (
        <>
          <SprintSelector
            sprints={sprints}
            selectedSprint={selectedSprint}
            onChange={handleSprintChange}
          />

          <EntryModeToggle entryMode={entryMode} onChange={handleEntryModeChange} />

          {entryMode === 'manual' ? (
            <ManualEntryForm entries={manualEntries} onChange={setManualEntries} />
          ) : (
            <AutoTaskSelect
              tasks={autoTasks}
              selectedTaskIds={selectedTaskIds}
              onToggleTask={handleToggleTask}
              extraEntries={extraEntries}
              onExtraEntriesChange={setExtraEntries}
              isLoading={isLoadingTasks}
            />
          )}

          <FileNameInput value={customFilename} onChange={setCustomFilename} />

          {error && (
            <div className="badge-warning" style={{ marginTop: 12 }}>
              {error}
            </div>
          )}

          <div style={{ marginTop: 10 }}>
            <GenerateButton isGenerating={isGenerating} onClick={handleGenerate} />
          </div>
        </>
      )}

      <CurrentItems entries={submittedEntries} />
      <GeneratedNotes
        notes={generatedNotes}
        wasChunked={wasChunked}
        savedFilename={savedFilename}
        onStartOver={handleStartOver}
      />

      <PastSprintNotes savedNotes={savedNotes} onNotesChanged={handleNotesChanged} />
    </div>
  );
}

export default App;

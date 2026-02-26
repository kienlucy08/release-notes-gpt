import { useState } from 'react';
import TagSelect from './TagSelect';

export default function AutoTaskSelect({
  tasks,
  selectedTaskIds,
  onToggleTask,
  extraEntries,
  onExtraEntriesChange,
  isLoading,
}) {
  function toggleAll(checked) {
    const allIds = new Set(checked ? tasks.map((t) => t.id) : []);
    // Replace all at once
    for (const task of tasks) {
      onToggleTask(task.id, checked);
    }
  }

  function updateExtra(index, field, value) {
    const updated = [...extraEntries];
    updated[index] = { ...updated[index], [field]: value };
    onExtraEntriesChange(updated);
  }

  function addExtraRow() {
    onExtraEntriesChange([...extraEntries, { tag: 'Feature', description: '' }]);
  }

  function removeExtraRow(index) {
    onExtraEntriesChange(extraEntries.filter((_, i) => i !== index));
  }

  if (isLoading) {
    return <div className="spinner">Loading tasks...</div>;
  }

  return (
    <div>
      <label>Select Tasks to Include:</label>
      {tasks.length === 0 ? (
        <p>No tasks found for this sprint.</p>
      ) : (
        <>
          <div style={{ marginBottom: 8 }}>
            <button
              type="button"
              className="button-third"
              onClick={() => toggleAll(true)}
            >
              Select All
            </button>
            <button
              type="button"
              className="button-third"
              onClick={() => toggleAll(false)}
            >
              Deselect All
            </button>
          </div>
          <ul className="task-list">
            {tasks.map((task) => (
              <li key={task.id}>
                <label>
                  <input
                    type="checkbox"
                    checked={selectedTaskIds.has(task.id)}
                    onChange={(e) => onToggleTask(task.id, e.target.checked)}
                  />
                  {task.name}
                </label>
              </li>
            ))}
          </ul>
        </>
      )}

      <div style={{ marginTop: 20 }}>
        <label>Add Additional Tasks:</label>
        {extraEntries.map((entry, i) => (
          <div key={i} className="entry-block">
            <button
              type="button"
              className="button-secondary"
              onClick={() => removeExtraRow(i)}
              style={{ float: 'right' }}
            >
              Remove Entry
            </button>
            <TagSelect
              value={entry.tag}
              onChange={(tag) => updateExtra(i, 'tag', tag)}
              namePrefix="extra_type"
            />
            <label>Description</label>
            <textarea
              className="input-area"
              placeholder="Enter description..."
              value={entry.description}
              onChange={(e) => updateExtra(i, 'description', e.target.value)}
            />
          </div>
        ))}
        <button type="button" className="button-secondary" onClick={addExtraRow}>
          Add Another
        </button>
      </div>
    </div>
  );
}

import TagSelect from './TagSelect';

export default function ManualEntryForm({ entries, onChange }) {
  function updateEntry(index, field, value) {
    const updated = [...entries];
    updated[index] = { ...updated[index], [field]: value };
    onChange(updated);
  }

  function addEntry() {
    onChange([...entries, { tag: 'Feature', description: '' }]);
  }

  function removeEntry(index) {
    onChange(entries.filter((_, i) => i !== index));
  }

  return (
    <div id="manual-entry-fields">
      {entries.map((entry, i) => (
        <div key={i} className="entry-block">
          {entries.length > 1 && (
            <button
              type="button"
              className="button-secondary"
              onClick={() => removeEntry(i)}
              style={{ float: 'right' }}
            >
              Remove Entry
            </button>
          )}
          <TagSelect
            value={entry.tag}
            onChange={(tag) => updateEntry(i, 'tag', tag)}
          />
          <label>Description</label>
          <textarea
            className="input-area"
            placeholder="Enter description..."
            value={entry.description}
            onChange={(e) => updateEntry(i, 'description', e.target.value)}
          />
        </div>
      ))}
      <button type="button" className="button-secondary" onClick={addEntry}>
        Add Another
      </button>
    </div>
  );
}

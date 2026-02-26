export default function EntryModeToggle({ entryMode, onChange }) {
  return (
    <div className="entry-block">
      <label>Task Entry Mode:</label>
      <div className="radio-group">
        <input
          type="radio"
          name="entry_mode"
          id="manual_mode"
          value="manual"
          checked={entryMode === 'manual'}
          onChange={() => onChange('manual')}
        />
        <label htmlFor="manual_mode">Manual</label>
        <input
          type="radio"
          name="entry_mode"
          id="auto_mode"
          value="auto"
          checked={entryMode === 'auto'}
          onChange={() => onChange('auto')}
        />
        <label htmlFor="auto_mode">Auto from Sprint</label>
      </div>
    </div>
  );
}

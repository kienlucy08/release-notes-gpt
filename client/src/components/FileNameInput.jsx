export default function FileNameInput({ value, onChange }) {
  return (
    <div>
      <label htmlFor="custom_filename">Custom File Name (optional):</label>
      <input
        type="text"
        name="custom_filename"
        className="input-area"
        placeholder="e.g. release_notes_july01_bugfixes"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

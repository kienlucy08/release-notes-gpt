export default function SprintSelector({ sprints, selectedSprint, onChange }) {
  return (
    <div className="entry-block">
      <label htmlFor="sprint">Select Sprint</label>
      <select
        name="sprint"
        className="input-select"
        value={selectedSprint}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">-- Select a Sprint --</option>
        {sprints.map((sprint) => (
          <option key={sprint.id} value={sprint.id}>
            {sprint.name}
          </option>
        ))}
      </select>
    </div>
  );
}

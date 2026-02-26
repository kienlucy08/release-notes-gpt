import { downloadAsFile, openInNewTab } from '../utils/fileExport';

export default function GeneratedNotes({ notes, wasChunked, savedFilename, onStartOver }) {
  if (!notes) return null;

  return (
    <>
      <h2 className="section-title">Generated Release Notes</h2>

      {wasChunked && (
        <div className="badge-warning">
          Heads up: Your notes were very long, so we split them into multiple chunks to
          generate properly.
        </div>
      )}

      <div className="output-box">{notes}</div>

      <div className="badge-success">Notes saved to browser storage.</div>

      <div style={{ marginTop: 20, display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        <button
          type="button"
          className="button-primary"
          onClick={() => openInNewTab(notes, savedFilename || 'release_notes.txt')}
        >
          Open in New Tab
        </button>
        <button
          type="button"
          className="button-secondary"
          onClick={() => downloadAsFile(notes, savedFilename || 'release_notes.txt')}
        >
          Download .txt
        </button>
        <button type="button" className="button-secondary" onClick={onStartOver}>
          Start Over
        </button>
      </div>
    </>
  );
}

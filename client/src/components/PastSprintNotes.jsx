import { useState } from 'react';
import { getNoteContent, deleteSingleNote, deleteAllNotes, renameNote } from '../utils/storage';
import { downloadAsFile, openInNewTab } from '../utils/fileExport';

export default function PastSprintNotes({ savedNotes, onNotesChanged }) {
  const [renamingFile, setRenamingFile] = useState(null);
  const [renameValue, setRenameValue] = useState('');
  const [viewingNote, setViewingNote] = useState(null);

  if (!savedNotes || savedNotes.length === 0) return null;

  function handleDeleteAll(folderId) {
    if (!window.confirm('Delete all release notes for this sprint?')) return;
    deleteAllNotes(folderId);
    onNotesChanged();
  }

  function handleDeleteSingle(folderId, filename) {
    if (!window.confirm('Delete this individual note?')) return;
    deleteSingleNote(folderId, filename);
    onNotesChanged();
  }

  function startRename(folderId, filename) {
    setRenamingFile({ folderId, filename });
    setRenameValue(filename.replace(/\.txt$/, ''));
  }

  function submitRename() {
    if (!renameValue.trim()) return;
    let newName = renameValue.trim();
    if (!newName.endsWith('.txt')) newName += '.txt';
    renameNote(renamingFile.folderId, renamingFile.filename, newName);
    setRenamingFile(null);
    setRenameValue('');
    onNotesChanged();
  }

  function handleView(folderId, filename) {
    if (viewingNote?.folderId === folderId && viewingNote?.filename === filename) {
      setViewingNote(null);
      return;
    }
    const content = getNoteContent(folderId, filename);
    setViewingNote({ folderId, filename, content });
  }

  return (
    <>
      <h2 className="section-title">Past Sprint Notes</h2>
      <ul>
        {savedNotes.map((sprint) => (
          <li key={sprint.folder} className="item-card">
            <strong>{sprint.name}</strong>
            <button
              type="button"
              className="button-secondary"
              style={{ marginLeft: 12 }}
              onClick={() => handleDeleteAll(sprint.folder)}
            >
              Delete Notes
            </button>
            <ul>
              {sprint.files.map((file) => {
                const isRenaming =
                  renamingFile?.folderId === sprint.folder &&
                  renamingFile?.filename === file;

                return (
                  <li key={file} className="file-item">
                    {isRenaming ? (
                      <div className="rename-form">
                        <input
                          type="text"
                          className="input-rename"
                          value={renameValue}
                          onChange={(e) => setRenameValue(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && submitRename()}
                          autoFocus
                          style={{ width: 180, fontSize: 13, padding: '3px 5px' }}
                        />
                        <button
                          type="button"
                          className="button-third"
                          onClick={submitRename}
                        >
                          Save
                        </button>
                        <button
                          type="button"
                          className="button-third"
                          onClick={() => setRenamingFile(null)}
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <>
                        <span
                          className="file-name"
                          style={{ cursor: 'pointer', textDecoration: 'underline', color: '#4338CA' }}
                          onClick={() => handleView(sprint.folder, file)}
                        >
                          {file}
                        </span>
                        <button
                          type="button"
                          className="button-third"
                          onClick={() => {
                            const content = getNoteContent(sprint.folder, file);
                            if (content) openInNewTab(content, file);
                          }}
                          title="Open in new tab"
                        >
                          Open
                        </button>
                        <button
                          type="button"
                          className="button-third"
                          onClick={() => {
                            const content = getNoteContent(sprint.folder, file);
                            if (content) downloadAsFile(content, file);
                          }}
                          title="Download as .txt file"
                        >
                          Download
                        </button>
                        <button
                          type="button"
                          className="button-third"
                          onClick={() => startRename(sprint.folder, file)}
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          className="button-third"
                          onClick={() => handleDeleteSingle(sprint.folder, file)}
                        >
                          Delete
                        </button>
                      </>
                    )}
                    {viewingNote?.folderId === sprint.folder &&
                      viewingNote?.filename === file && (
                        <div className="output-box" style={{ marginTop: 10 }}>
                          {viewingNote.content}
                        </div>
                      )}
                  </li>
                );
              })}
            </ul>
          </li>
        ))}
      </ul>
    </>
  );
}

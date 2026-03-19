/**
 * Downloads text content as a .txt file.
 */
export function downloadAsFile(content, filename = 'release_notes.txt') {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename.endsWith('.txt') ? filename : `${filename}.txt`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Opens the note content in a new browser tab as a clean, readable page
 * that's easy to select-all and copy into a Word document.
 */
export function openInNewTab(content, filename = 'release_notes.txt') {
  const newWindow = window.open('', '_blank');
  if (!newWindow) {
    alert('Popup blocked. Please allow popups for this site.');
    return;
  }

  newWindow.document.write(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${escapeHtml(filename)}</title>
  <style>
    body {
      font-family: 'Segoe UI', Calibri, Arial, sans-serif;
      max-width: 900px;
      margin: 40px auto;
      padding: 0 24px;
      color: #1a1a1a;
      line-height: 1.6;
      background: #fff;
    }
    h1 {
      font-size: 20px;
      color: #4338CA;
      border-bottom: 2px solid #4338CA;
      padding-bottom: 8px;
      margin-bottom: 24px;
    }
    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
      font-family: 'Segoe UI', Calibri, Arial, sans-serif;
      font-size: 14px;
      line-height: 1.7;
    }
    .actions {
      margin-bottom: 20px;
      display: flex;
      gap: 10px;
    }
    .actions button {
      padding: 8px 16px;
      border: 1px solid #CBD5E1;
      border-radius: 6px;
      background: #F1F5F9;
      cursor: pointer;
      font-size: 13px;
    }
    .actions button:hover {
      background: #E2E8F0;
    }
    @media print {
      .actions { display: none; }
    }
  </style>
</head>
<body>
  <h1>${escapeHtml(filename)}</h1>
  <div class="actions">
    <button onclick="document.querySelector('pre').focus();document.execCommand('selectAll');document.getSelection().selectAllChildren(document.querySelector('pre'))">Select All</button>
    <button onclick="window.print()">Print</button>
  </div>
  <pre>${escapeHtml(content)}</pre>
</body>
</html>`);
  newWindow.document.close();
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

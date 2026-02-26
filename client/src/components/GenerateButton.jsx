export default function GenerateButton({ isGenerating, onClick }) {
  return (
    <button
      type="button"
      className={`button-primary${isGenerating ? ' loading' : ''}`}
      disabled={isGenerating}
      onClick={onClick}
    >
      {isGenerating ? 'Generating...' : 'Generate Release Notes'}
    </button>
  );
}

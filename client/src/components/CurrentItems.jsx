export default function CurrentItems({ entries }) {
  if (!entries || entries.length === 0) return null;

  return (
    <>
      <h2 className="section-title">Current Items</h2>
      <ul>
        {entries.map((item, i) => (
          <li key={i} className="item-card">
            {item}
          </li>
        ))}
      </ul>
    </>
  );
}

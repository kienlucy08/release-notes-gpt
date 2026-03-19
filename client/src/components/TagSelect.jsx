import { useState } from 'react';

const TAG_OPTIONS = ['Feature', 'Bug', 'Enhancement', 'DevOps', 'Combination'];
const SUB_TAG_OPTIONS = ['Feature', 'Bug', 'Enhancement', 'DevOps'];

export default function TagSelect({ value, onChange, namePrefix = 'type' }) {
  const isCombination = value.startsWith('Combination');
  const [subTag1, setSubTag1] = useState('Feature');
  const [subTag2, setSubTag2] = useState('Bug');

  function handlePrimaryChange(e) {
    const selected = e.target.value;
    if (selected === 'Combination') {
      onChange(`Combination (${subTag1} & ${subTag2})`);
    } else {
      onChange(selected);
    }
  }

  function handleSubTag1Change(e) {
    const newSub1 = e.target.value;
    setSubTag1(newSub1);
    onChange(`Combination (${newSub1} & ${subTag2})`);
  }

  function handleSubTag2Change(e) {
    const newSub2 = e.target.value;
    setSubTag2(newSub2);
    onChange(`Combination (${subTag1} & ${newSub2})`);
  }

  const primaryValue = isCombination ? 'Combination' : value;

  return (
    <>
      <label>Tag</label>
      <select
        name={namePrefix}
        className="input-select"
        value={primaryValue}
        onChange={handlePrimaryChange}
      >
        {TAG_OPTIONS.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>

      {isCombination && (
        <>
          <label>Specify Your Combination of Tags</label>
          <select
            className="input-select-hidden"
            style={{ display: 'block' }}
            value={subTag1}
            onChange={handleSubTag1Change}
          >
            {SUB_TAG_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
          <select
            className="input-select-hidden"
            style={{ display: 'block' }}
            value={subTag2}
            onChange={handleSubTag2Change}
          >
            {SUB_TAG_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </>
      )}
    </>
  );
}

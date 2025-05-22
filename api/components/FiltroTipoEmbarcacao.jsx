import React from 'react';

const FiltroTipoEmbarcacao = ({ selectedTypes, setSelectedTypes }) => {
  const shipTypes = {
    0: "Cargo",
    1: "Cruise",
    2: "Military",
    3: "Offshore",
    4: "Passenger",
    5: "Tanker",
    6: "Tug"
  };

  const handleChange = (e) => {
    const value = parseInt(e.target.value);
    if (selectedTypes.includes(value)) {
      setSelectedTypes(selectedTypes.filter((type) => type !== value));
    } else {
      setSelectedTypes([...selectedTypes, value]);
    }
  };

  return (
    <div>
      <h3>Filtrar por tipo de embarcação:</h3>
      {Object.entries(shipTypes).map(([key, label]) => (
        <label key={key} style={{ marginRight: '10px' }}>
          <input
            type="checkbox"
            value={key}
            checked={selectedTypes.includes(parseInt(key))}
            onChange={handleChange}
          />
          {label}
        </label>
      ))}
    </div>
  );
};

export default FiltroTipoEmbarcacao;

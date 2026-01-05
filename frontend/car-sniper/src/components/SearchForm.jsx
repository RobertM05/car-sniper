import React from 'react';

const SearchForm = ({
  formData,
  setFormData,
  brands,
  models,
  generations,
  loadingBrands,
  loadingModels,
  loadingGenerations,
  onSubmit,
  loading,
  onAlertClick
}) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <form onSubmit={onSubmit} className="glass-panel search-form-grid">
      <div className="form-group">
        <label>Marca</label>
        <select
          name="make"
          value={formData.make}
          onChange={handleChange}
          className="form-control"
        >
          <option value="">Selectează marca</option>
          {brands.map((brand) => (
            <option key={brand} value={brand}>{brand}</option>
          ))}
        </select>
        {loadingBrands && <small className="text-secondary">Se încarcă...</small>}
      </div>

      <div className="form-group">
        <label>Model</label>
        <select
          name="model"
          value={formData.model}
          onChange={handleChange}
          disabled={!formData.make || loadingModels}
          className="form-control"
        >
          <option value="">Selectează modelul</option>
          {models.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
        {loadingModels && <small className="text-secondary">Se încarcă...</small>}
      </div>

      {generations.length > 0 && (
        <div className="form-group">
          <label>Generația</label>
          <select
            name="generation"
            value={formData.generation}
            onChange={handleChange}
            disabled={!formData.model || loadingGenerations}
            className="form-control"
          >
            <option value="">Oricare</option>
            {generations.map((g) => (
              <option key={g.generation} value={g.generation}>
                {g.generation} ({g.min_year}-{g.max_year})
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="form-group">
        <label>Preț Min (€)</label>
        <input
          type="number"
          name="minPrice"
          value={formData.minPrice}
          onChange={handleChange}
          placeholder="0"
          className="form-control"
        />
      </div>

      <div className="form-group">
        <label>Preț Max (€)</label>
        <input
          type="number"
          name="maxPrice"
          value={formData.maxPrice}
          onChange={handleChange}
          placeholder="50000"
          className="form-control"
        />
      </div>

      <div className="form-group">
        <label>An Min</label>
        <input
          type="number"
          name="minYear"
          value={formData.minYear}
          onChange={handleChange}
          placeholder="2010"
          className="form-control"
        />
      </div>

      <div className="form-group">
        <label>An Max</label>
        <input
          type="number"
          name="maxYear"
          value={formData.maxYear}
          onChange={handleChange}
          placeholder="2024"
          className="form-control"
        />
      </div>

      <div className="form-group">
        <label>Km Max</label>
        <input
          type="number"
          name="maxKm"
          value={formData.maxKm}
          onChange={handleChange}
          placeholder="200000"
          className="form-control"
        />
      </div>

      <div className="form-group">
        <label>Limită Anunțuri</label>
        <select
          name="limit"
          value={formData.limit}
          onChange={handleChange}
          className="form-control"
        >
          <option value="50">Rapid (50)</option>
          <option value="100">Normal (100)</option>
          <option value="300">Extins (300)</option>
          <option value="1000">Maxim (Toate)</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={loading || !formData.make || !formData.model}
        className="submit-btn"
        title={(!formData.make || !formData.model) ? "Selectează Marca și Modelul" : ""}
      >
        {loading ? "Se caută..." : "🔍 Caută Mașina Perfectă"}
      </button>

      <button
        type="button"
        onClick={onAlertClick}
        disabled={!formData.make || !formData.model}
        className="submit-btn"
        style={{
          marginTop: '0.5rem',
          background: 'transparent',
          border: '2px solid rgba(56, 189, 248, 0.5)',
          color: 'var(--primary-color)'
        }}
        title={(!formData.make || !formData.model) ? "Selectează Marca și Modelul" : ""}
      >
        🔔 Setează Alertă Preț
      </button>
    </form>
  );
};

export default SearchForm;

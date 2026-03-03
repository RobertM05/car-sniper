import React, { useState } from "react";
import { useLanguage } from "../LanguageContext";

const SearchForm = ({
  formData,
  setFormData,
  brands,
  models,
  loadingBrands,
  loadingModels,
  onSubmit,
  loading,
  onAlertClick
}) => {
  const { t } = useLanguage();
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => {
      const newData = { ...prev, [name]: value };
      if (name === "make") {
        newData.model = "";
        newData.generation = "";
      }
      if (name === "model") {
        newData.generation = "";
      }
      return newData;
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="search-form-grid glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

      {/* Top Row: 4 Columns */}
      <div style={{ width: '100%', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
        <div className="form-group">
          <label>{t('search', 'make')}</label>
          <select
            name="make"
            value={formData.make}
            onChange={handleChange}
            disabled={loadingBrands}
            className="form-control"
          >
            <option value="">{t('search', 'anyMake')}</option>
            {brands.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>{t('search', 'model')}</label>
          <select
            name="model"
            value={formData.model}
            onChange={handleChange}
            disabled={!formData.make || loadingModels}
            className="form-control"
          >
            <option value="">{t('search', 'anyModel')}</option>
            {models.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>{t('search', 'minPrice')}</label>
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
          <label>{t('search', 'maxPrice')}</label>
          <input
            type="number"
            name="maxPrice"
            value={formData.maxPrice}
            onChange={handleChange}
            placeholder="100000"
            className="form-control"
          />
        </div>
      </div>

      {/* Advanced Row: 4 Columns */}
      {showAdvanced && (
        <div style={{ width: '100%', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1.5rem' }}>
          <div className="form-group">
            <label>{t('search', 'minYear')}</label>
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
            <label>{t('search', 'maxYear')}</label>
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
            <label>{t('search', 'maxKm')}</label>
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
            <label>{t('search', 'limit')}</label>
            <select
              name="limit"
              value={formData.limit}
              onChange={handleChange}
              className="form-control"
            >
              <option value="50">{t('search', 'fast')}</option>
              <option value="100">{t('search', 'normal')}</option>
              <option value="300">{t('search', 'extended')}</option>
              <option value="1000">{t('search', 'all')}</option>
            </select>
          </div>
        </div>
      )}

      {/* Action Buttons Centered Below */}
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1rem', width: '100%', paddingTop: showAdvanced ? '1.5rem' : '1rem' }}>
        <button
          type="button"
          onClick={onAlertClick}
          disabled={!formData.make || !formData.model}
          className="submit-btn"
          style={{ background: 'transparent', border: '1px solid var(--primary-color)', color: 'var(--primary-color)' }}
        >
          {t('search', 'setAlert')}
        </button>

        <button
          type="submit"
          disabled={loading}
          className="submit-btn"
          style={{ paddingLeft: '3rem', paddingRight: '3rem' }}
        >
          {loading ? t('search', 'searching') : t('search', 'searchBtn')}
        </button>

        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="submit-btn"
          style={{ background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-primary)', whiteSpace: 'nowrap' }}
        >
          {t('search', 'advanced')}
        </button>
      </div>

    </form>
  );
};

export default SearchForm;

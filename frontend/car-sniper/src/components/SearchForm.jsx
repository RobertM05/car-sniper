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
    <div className="search-form-shell">
      <form onSubmit={handleSubmit} className="search-form-grid">

        {/* Top Row: 4 Columns */}
        <div className="search-fields-row">
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
          <div className="search-fields-row search-fields-advanced">
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
              <label>Combustibil</label>
              <select name="fuel" value={formData.fuel || ""} onChange={handleChange} className="form-control">
                <option value="">Oricare</option>
                <option value="Petrol">Benzină</option>
                <option value="Diesel">Diesel</option>
                <option value="Hybrid">Hibrid</option>
                <option value="Electric">Electric</option>
              </select>
            </div>

            <div className="form-group">
              <label>Cutie de viteze</label>
              <select name="transmission" value={formData.transmission || ""} onChange={handleChange} className="form-control">
                <option value="">Oricare</option>
                <option value="Automatic">Automată</option>
                <option value="Manual">Manuală</option>
              </select>
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
        <div className="search-actions-row">
          <button
            type="button"
            onClick={onAlertClick}
            disabled={!formData.make || !formData.model}
            className="submit-btn"
            style={{ background: 'transparent', border: '1px solid var(--border-shell)', color: 'var(--text-secondary)', paddingRight: '1.5rem' }}
          >
            {t('search', 'setAlert')}
          </button>

          <button
            type="submit"
            disabled={loading}
            className="submit-btn"
          >
            {loading ? t('search', 'searching') : t('search', 'searchBtn')}
            <div className="submit-btn-inner">
              &rarr;
            </div>
          </button>

          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="submit-btn"
            style={{ background: 'transparent', border: '1px solid var(--border-shell)', color: 'var(--text-secondary)', paddingRight: '1.5rem' }}
          >
            {t('search', 'advanced')}
          </button>
        </div>

      </form>
    </div>
  );
};

export default SearchForm;

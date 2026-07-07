import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import PropTypes from 'prop-types';
import { useLanguage } from '../LanguageContext';

const FilterSidebar = ({ filters, onFilterChange, onApply, isOpen, onClose }) => {
    const { t } = useLanguage();
    const [localFilters, setLocalFilters] = useState(filters);

    useEffect(() => {
        setLocalFilters(filters);
    }, [filters]);

    const handleChange = (key, value) => {
        setLocalFilters(prev => ({ ...prev, [key]: value }));
    };

    const handleCheckbox = (key, value) => {
        setLocalFilters(prev => {
            const current = prev[key] || [];
            if (current.includes(value)) {
                return { ...prev, [key]: current.filter(v => v !== value) };
            }
            return { ...prev, [key]: [...current, value] };
        });
    };

    const handleApply = () => {
        onFilterChange(localFilters);
        onApply();
        if (onClose) onClose();
    };

    return (
        <aside id="filter-sidebar" className={`filter-sidebar${isOpen ? ' open' : ''}`}>
            <button className="filter-sidebar-close" onClick={onClose} aria-label="Close filters">
                <X size={20} />
            </button>

            <div className="filter-section">
                <label className="filter-label" htmlFor="filter-minPrice">{t('filters', 'price')}</label>
                <div className="filter-two-col">
                    <input type="number" placeholder={t('filters', 'min')} className="filter-input"
                        value={localFilters.minPrice || ''}
                        onChange={e => handleChange('minPrice', e.target.value)} />
                    <input type="number" placeholder={t('filters', 'max')} className="filter-input"
                        value={localFilters.maxPrice || ''}
                        onChange={e => handleChange('maxPrice', e.target.value)} />
                </div>
            </div>

            <div className="filter-section">
                <label className="filter-label" htmlFor="filter-minYear">{t('filters', 'year')}</label>
                <div className="filter-two-col">
                    <input type="number" placeholder={t('filters', 'from')} className="filter-input"
                        value={localFilters.minYear || ''}
                        onChange={e => handleChange('minYear', e.target.value)} />
                    <input type="number" placeholder={t('filters', 'to')} className="filter-input"
                        value={localFilters.maxYear || ''}
                        onChange={e => handleChange('maxYear', e.target.value)} />
                </div>
            </div>

            <div className="filter-section">
                <label className="filter-label" htmlFor="filter-maxKm">{t('filters', 'maxKm')}</label>
                <input type="number" className="filter-input"
                    id="filter-maxKm"
                    value={localFilters.maxKm || ''}
                    onChange={e => handleChange('maxKm', e.target.value)} />
            </div>

            <div className="filter-section">
                <label className="filter-label">{t('filters', 'fuel')}</label>
                <div className="filter-checkbox-group">
                    {['Petrol', 'Diesel', 'Hybrid', 'Electric'].map(fuel => (
                        <label key={fuel} className="filter-checkbox-label">
                            <input type="checkbox"
                                checked={(localFilters.fuel || []).includes(fuel)}
                                onChange={() => handleCheckbox('fuel', fuel)} />
                            {t('filters', fuel.toLowerCase())}
                        </label>
                    ))}
                </div>
            </div>

            <div className="filter-section">
                <label className="filter-label">{t('filters', 'transmission')}</label>
                <div className="filter-checkbox-group">
                    {['Automatic', 'Manual'].map(trans => (
                        <label key={trans} className="filter-checkbox-label">
                            <input type="checkbox"
                                checked={(localFilters.transmission || []).includes(trans)}
                                onChange={() => handleCheckbox('transmission', trans)} />
                            {t('filters', trans.toLowerCase())}
                        </label>
                    ))}
                </div>
            </div>

            <div className="filter-section">
                <label className="filter-label">{t('filters', 'source')}</label>
                <div className="filter-checkbox-group">
                    <label className="filter-checkbox-label">
                        <input type="checkbox"
                            checked={(localFilters.source || []).includes('verified')}
                            onChange={() => handleCheckbox('source', 'verified')} />
                        {t('filters', 'verifiedPartner') || 'Verified Partner'}
                    </label>
                </div>
                <div className="filter-checkbox-group">
                    {['OLX.ro', 'Autovit.ro'].map(src => (
                        <label key={src} className="filter-checkbox-label">
                            <input type="checkbox"
                                checked={(localFilters.source || []).includes(src)}
                                onChange={() => handleCheckbox('source', src)} />
                            {src}
                        </label>
                    ))}
                </div>
            </div>

            <button className="filter-clear-btn" onClick={() => {
                const cleared = { minPrice: '', maxPrice: '', minYear: '', maxYear: '', maxKm: '', fuel: [], transmission: [], source: [] };
                setLocalFilters(cleared);
                onFilterChange(cleared);
            }}>
                {t('filters', 'clearAll')}
            </button>
            <button className="filter-apply-btn" onClick={handleApply}>
                {t('filters', 'apply')}
            </button>
        </aside>
    );
};

FilterSidebar.propTypes = {
    filters: PropTypes.object.isRequired,
    onFilterChange: PropTypes.func.isRequired,
    onApply: PropTypes.func.isRequired,
    isOpen: PropTypes.bool,
    onClose: PropTypes.func,
};

export default FilterSidebar;

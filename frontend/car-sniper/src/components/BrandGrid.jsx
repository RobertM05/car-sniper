import React from 'react';
import { useLanguage } from '../LanguageContext';

// Static list for MVP — wire to /api/brands for dynamic brands
const POPULAR_BRANDS = [
    'Dacia', 'BMW', 'Mercedes', 'Audi', 'VW', 'Skoda', 'Ford', 'Toyota',
    'Hyundai', 'Kia', 'Renault', 'Volvo', 'Opel', 'Peugeot', 'Tesla', 'Mazda',
];

const BrandGrid = ({ onBrandSelect }) => {
    const { t } = useLanguage();
    return (
        <section className="brand-grid-section">
            <h2 className="brand-grid-title">{t('brands', 'popularBrands')}</h2>
            <div className="brand-grid">
                {POPULAR_BRANDS.map((brand) => (
                    <button
                        key={brand}
                        className="brand-chip"
                        onClick={() => onBrandSelect(brand)}
                    >
                        {brand}
                    </button>
                ))}
            </div>
        </section>
    );
};

export default BrandGrid;

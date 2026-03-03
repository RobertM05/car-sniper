import React from 'react';
import { useLanguage } from '../LanguageContext';

const CarCard = ({ car }) => {
    const { t } = useLanguage();

    let displayPrice = "";
    const rawPrice = parseInt(String(car.price).replace(/\D/g, '')) || 0;

    if (rawPrice === 0) {
        displayPrice = t('card', 'priceOnRequest');
    } else {
        displayPrice = new Intl.NumberFormat('ro-RO', {
            style: 'currency',
            currency: 'EUR',
            maximumFractionDigits: 0
        }).format(rawPrice);
    }

    const isOlx = (car.link || car.url || "").includes('olx');
    const siteName = car.subsource || car.source || (isOlx ? 'OLX' : 'Autovit');
    const badgeClass = isOlx ? 'badge-olx' : 'badge-autovit';

    return (
        <div className="glass-panel car-card">
            <div className={`site-badge ${badgeClass}`}>
                {siteName}
            </div>

            <div className="car-image-container">
                <img
                    src={car.image || "https://placehold.co/600x400/1e293b/cbd5e1?text=Fără+Poză"}
                    alt={car.title}
                    className="car-image"
                    loading="lazy"
                    referrerPolicy="no-referrer"
                    onError={(e) => { e.target.onerror = null; e.target.src = "https://placehold.co/600x400/1e293b/cbd5e1?text=Eroare+Poză"; }}
                />
            </div>

            <div className="car-content">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <h3 className="car-title" title={car.title || car.name}>
                        {car.title || car.name || t('card', 'noTitle')}
                    </h3>
                    <div className={`price ${rawPrice === 0 ? 'text-warning' : ''}`}>
                        {displayPrice}
                    </div>
                </div>

                <div className="car-specs">
                    {car.year && (
                        <span className="spec-chip">
                            {car.year}
                        </span>
                    )}
                    {car.km && (
                        <span className="spec-chip">
                            {car.km} km
                        </span>
                    )}
                    {car.fuel && (
                        <span className="spec-chip">
                            {car.fuel}
                        </span>
                    )}
                </div>
            </div>


            <a
                href={car.url || car.link}
                target="_blank"
                rel="noreferrer"
                className="car-link-overlay"
                style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 1, opacity: 0 }}
                aria-label={`Vezi anunț: ${car.title}`}
            ></a>
        </div>
    );
};

export default CarCard;

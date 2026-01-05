import React from 'react';

const CarCard = ({ car }) => {
    // Format price
    let displayPrice = "";
    const rawPrice = parseInt(String(car.price).replace(/\D/g, '')) || 0;

    if (rawPrice === 0) {
        displayPrice = "Preț la cerere";
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
                <h3 className="car-title" title={car.title || car.name}>
                    {car.title || car.name || "Anunț fără titlu"}
                </h3>

                <div className="car-specs">
                    {car.year && (
                        <span className="spec-chip">
                            📅 {car.year}
                        </span>
                    )}
                    {car.km && (
                        <span className="spec-chip">
                            🛣️ {car.km} km
                        </span>
                    )}
                    {car.fuel && (
                        <span className="spec-chip">
                            ⛽ {car.fuel}
                        </span>
                    )}
                </div>

                <div className="car-footer">
                    <div className={`price ${rawPrice === 0 ? 'text-warning' : ''}`}>
                        {displayPrice}
                    </div>
                    <a
                        href={car.url || car.link}
                        target="_blank"
                        rel="noreferrer"
                        className="view-btn"
                    >
                        Vezi Anunț <span>→</span>
                    </a>
                </div>
            </div>

            {/* Full card clickable overlay for better UX on mobile */}
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

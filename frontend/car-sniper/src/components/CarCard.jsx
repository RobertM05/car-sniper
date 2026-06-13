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
    
    // Deal Score Logic
    let dealClass = "";
    let dealTextKey = "";
    if (car.deal_score != null) {
        if (car.deal_score >= 80) { dealClass = "deal-excellent"; dealTextKey = "excellent"; }
        else if (car.deal_score >= 60) { dealClass = "deal-good"; dealTextKey = "good"; }
        else if (car.deal_score >= 40) { dealClass = "deal-fair"; dealTextKey = "fair"; }
        else { dealClass = "deal-overpriced"; dealTextKey = "overpriced"; }
    }

    return (
        <div className="car-card-shell group">
            <div className="car-card-core">
                <div className={`site-badge ${badgeClass}`}>
                    {siteName}
                </div>
                
                {car.deal_score != null && (
                    <div className={`deal-badge ${dealClass} group/tooltip relative`}>
                        <div className="deal-score">{car.deal_score}</div>
                        <div className="deal-label">{t('deal', dealTextKey)}</div>
                        
                        {/* Tooltip Explanation */}
                        {car.peer_avg_price > 0 && (
                            <div className="absolute opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all duration-300 bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-[var(--bg-core)] border border-[var(--border-shell)] rounded-xl shadow-2xl z-50 text-left pointer-events-none">
                                <div className="text-[10px] uppercase tracking-wider text-[var(--primary-color)] font-bold mb-1">
                                    AI Deal Analysis
                                </div>
                                <p className="text-xs text-[var(--text-secondary)] m-0 leading-relaxed">
                                    This car is <strong className={car.price_diff > 0 ? "text-green-400" : "text-red-400"}>
                                        €{Math.abs(car.price_diff).toLocaleString()} {car.price_diff > 0 ? "cheaper" : "more expensive"}
                                    </strong> than the market average of €{car.peer_avg_price.toLocaleString()} for similar models.
                                </p>
                            </div>
                        )}
                    </div>
                )}

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
                        {car.title || car.name || t('card', 'noTitle')}
                    </h3>

                    <div className="car-specs">
                        {car.year && <span className="spec-chip">{car.year}</span>}
                        {car.km && <span className="spec-chip">{car.km} km</span>}
                        {car.fuel && <span className="spec-chip">{car.fuel}</span>}
                    </div>

                    <div className="car-footer">
                        <div className={`price ${rawPrice === 0 ? 'text-warning' : ''}`}>
                            {displayPrice}
                        </div>
                        <div style={{ color: "var(--text-secondary)", fontSize: "0.85rem", fontWeight: 600 }}>
                            Detalii &rarr;
                        </div>
                    </div>
                </div>

                <a
                    href={car.url || car.link}
                    target="_blank"
                    rel="noreferrer"
                    className="car-link-overlay"
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 10, opacity: 0 }}
                    aria-label={`Vezi anunț: ${car.title}`}
                ></a>
            </div>
        </div>
    );
};

export default CarCard;

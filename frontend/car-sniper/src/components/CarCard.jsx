import React, { useState } from 'react';
import { useLanguage } from '../LanguageContext';
import PropTypes from 'prop-types';
import { toggleCompareCar, isCarCompared } from '../utils/carComparison';

const CarCard = ({ car, index = 0 }) => {
    const { t } = useLanguage();
    const [tooltipOpen, setTooltipOpen] = useState(false);
    const [compared, setCompared] = useState(isCarCompared(car));

    let displayPrice = "";
    const rawPrice = parseInt(String(car.price).replace(/\D/g, '')) || 0;
    const rawOriginalPrice = parseInt(String(car.original_price).replace(/\D/g, '')) || rawPrice;

    const priceDrop = (rawOriginalPrice > rawPrice && rawPrice > 0)
        ? Math.round(((rawOriginalPrice - rawPrice) / rawOriginalPrice) * 100)
        : 0;

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
        <div
            className="car-card-shell group"
            style={{
                animation: 'fadeUp 0.6s var(--spring-easing) forwards',
                opacity: 0,
                animationDelay: `${index * 0.05}s`
            }}
        >
            <div className="car-card-core">
                <button className="compare-btn" onClick={(e) => { e.preventDefault(); e.stopPropagation(); const cars = toggleCompareCar(car); setCompared(cars.some(c => c.id === car.id || c.link === (car.link || car.url))); }} title={compared ? "Remove from compare" : "Add to compare"}>{compared ? "★" : "☆"}</button>

                {car.is_verified_partner && (
                    <div className="verified-badge">
                        Partener Verificat
                    </div>
                )}

                <div className="car-image-container">
                    <img
                        src={car.image || "https://placehold.co/600x400/1e293b/cbd5e1?text=Fără+Poză"}
                        alt={car.title || car.name || 'Car listing'}
                        className="car-image"
                        loading="lazy"
                        referrerPolicy="no-referrer"
                        onError={(e) => { e.target.onerror = null; e.target.src = "https://placehold.co/600x400/1e293b/cbd5e1?text=Eroare+Poză"; }}
                    />

                    {car.deal_score != null && (
                        <div
                            className={`deal-ring ${dealClass} group/tooltip relative ${tooltipOpen ? 'is-open' : ''}`}
                            onClick={() => {
                                setTooltipOpen(!tooltipOpen);
                            }}
                        >
                            <div className="deal-score">{car.deal_score}</div>
                            <div className="deal-label">{t('deal', dealTextKey)}</div>

                            {/* Tooltip Explanation */}
                            {car.peer_avg_price > 0 && (
                                <div className="deal-tooltip">
                                    <div className="deal-tooltip-title">
                                        {t('deal', 'analysisTitle')}
                                    </div>
                                    <p className="deal-tooltip-text">
                                        This car is <strong style={{ color: car.price_diff > 0 ? '#4ade80' : '#f87171' }}>
                                            €{car.price_diff != null ? Math.abs(car.price_diff).toLocaleString() : '0'} {car.price_diff > 0 ? t('deal', 'cheaper') : t('deal', 'moreExpensive')}
                                        </strong> than the market average of €{car.peer_avg_price.toLocaleString()} for similar models.
                                    </p>
                                </div>
                            )}
                        </div>
                    )}

                    {priceDrop > 0 && (
                        <div className="price-drop-badge">
                            ↓ {t('card', 'priceDrop', { percent: priceDrop })}
                        </div>
                    )}
                </div>

                <div className="car-content">
                    <div className="car-header">
                        <h3 className="car-title" title={car.title || car.name}>
                            {car.title || car.name || t('card', 'noTitle')}
                        </h3>
                        <div className={`site-badge ${badgeClass}`}>
                            {siteName}
                        </div>
                    </div>

                    <div className="car-specs">
                        {car.year && <span className="spec-chip">{car.year}</span>}
                        {car.km != null && car.km !== '' && <span className="spec-chip">{car.km} km</span>}
                        {car.fuel && <span className="spec-chip">{car.fuel}</span>}
                    </div>

                    <div className="car-footer">
                        <div className={`price ${rawPrice === 0 ? 'text-warning' : ''}`}>
                            {displayPrice}
                        </div>
                        <div style={{ color: "var(--text-secondary)", fontSize: "0.85rem", fontWeight: 600 }}>
                            {t('card', 'viewDetails')} &rarr;
                        </div>
                    </div>
                </div>

                <a
                    href={car.url || car.link}
                    target="_blank"
                    rel="noreferrer"
                    className="car-link-overlay"
                    aria-label={`${t('deal', 'viewDealAriaLabel', { title: car.title })}`}
                ></a>
            </div>
        </div>
    );
};

CarCard.propTypes = {
    car: PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        title: PropTypes.string,
        name: PropTypes.string,
        price: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        original_price: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        price_diff: PropTypes.number,
        peer_avg_price: PropTypes.number,
        deal_score: PropTypes.number,
        year: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        km: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        fuel: PropTypes.string,
        transmission: PropTypes.string,
        trans: PropTypes.string,
        link: PropTypes.string,
        url: PropTypes.string,
        image: PropTypes.string,
        source: PropTypes.string,
        subsource: PropTypes.string,
        is_verified_partner: PropTypes.bool,
    }).isRequired,
    index: PropTypes.number,
};

export default CarCard;

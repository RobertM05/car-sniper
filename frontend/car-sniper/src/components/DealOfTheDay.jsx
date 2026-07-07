import React, { useState, useEffect } from 'react';
import CarCard from './CarCard';
import SkeletonCard from './SkeletonCard';
import { useLanguage } from '../LanguageContext';
import { getCached, setCache } from '../utils/cache';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

const DealOfTheDay = () => {
    const { t } = useLanguage();
    const [deals, setDeals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchDeals = async () => {
            try {
                const cached = getCached('top_deals');
                if (cached) {
                    setDeals(cached);
                    setLoading(false);
                    return;
                }
                setLoading(true);
                setError(null);
                const response = await fetch(`${API_BASE_URL}/api/deals/top`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                const data = await response.json();
                if (data.error) {
                    throw new Error(data.error);
                }
                setDeals(data.results || []);
                setCache('top_deals', data.results || []);
            } catch (err) {
                console.error("Failed to fetch top deals:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchDeals();
    }, []);

    if (loading) {
        return (
            <div className="deals-section-shell">
                <div className="deals-section-core">
                    <div className="deals-section-header">
                        <h2 className="deals-section-title">
                            {t('dealOfTheDay', 'title')}
                        </h2>
                        <p className="deals-section-subtitle">
                            {t('dealOfTheDay', 'loading')}
                        </p>
                    </div>
                    <div className="deals-grid">
                        {[...Array(8)].map((_, i) => (
                            <SkeletonCard key={i} />
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (error || deals.length === 0) {
        return null; // Gracefully hide if error occurs or no deals are active
    }

    return (
        <div className="deals-section-shell">
            <div className="deals-section-core">
                <div className="deals-section-header">
                    <h2 className="deals-section-title">
                        {t('dealOfTheDay', 'title')}
                    </h2>
                    <p className="deals-section-subtitle">
                        {t('dealOfTheDay', 'subtitle')}
                    </p>
                </div>
                {deals.length > 0 && (() => {
                    const top = deals[0];
                    const rawPrice = parseInt(String(top.price).replace(/\D/g, '')) || 0;
                    const displayPrice = rawPrice === 0 ? t('card', 'priceOnRequest')
                        : new Intl.NumberFormat('ro-RO', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(rawPrice);
                    const formattedSavings = top.price_diff > 0
                        ? new Intl.NumberFormat('ro-RO', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(top.price_diff)
                        : '';
                    let dealClass = '';
                    let dealTextKey = '';
                    if (top.deal_score != null) {
                        if (top.deal_score >= 80) { dealClass = 'deal-excellent'; dealTextKey = 'excellent'; }
                        else if (top.deal_score >= 60) { dealClass = 'deal-good'; dealTextKey = 'good'; }
                        else if (top.deal_score >= 40) { dealClass = 'deal-fair'; dealTextKey = 'fair'; }
                        else { dealClass = 'deal-overpriced'; dealTextKey = 'overpriced'; }
                    }
                    return (
                        <div className="dotd-featured-card">
                            <img
                                src={top.image || "https://placehold.co/600x400/1e293b/cbd5e1?text=No+Image"}
                                alt={top.title}
                                className="dotd-featured-image"
                                loading="lazy"
                                referrerPolicy="no-referrer"
                                onError={(e) => { e.target.onerror = null; e.target.src = "https://placehold.co/600x400/1e293b/cbd5e1?text=Error"; }}
                            />
                            <div className="dotd-featured-content">
                                <div style={{ flex: 1 }}>
                                    <div className="dotd-featured-meta">
                                        <span className="dotd-featured-source">{top.source || top.subsource || 'OLX'}</span>
                                    </div>
                                    <h3 className="dotd-featured-title">{top.title || top.name}</h3>
                                    <p className="dotd-featured-specs">
                                        {[top.km && top.km + ' km', top.year, top.fuel, top.transmission].filter(Boolean).join(' · ')}
                                    </p>
                                    <p className="dotd-featured-price">{displayPrice}</p>
                                    {top.price_diff > 0 && (
                                        <p className="dotd-featured-savings">
                                            {t('deal', 'savingsMessage', { amount: formattedSavings })}
                                        </p>
                                    )}
                                </div>
                                {top.deal_score != null && (
                                    <div className="dotd-featured-score-area">
                                        <div className={`deal-ring ${dealClass}`}>
                                            <div className="deal-score">{top.deal_score}</div>
                                            <div className="deal-label">{t('deal', dealTextKey)}</div>
                                        </div>
                                    </div>
                                )}
                            </div>
                            <a
                                href={top.url || top.link}
                                target="_blank"
                                rel="noreferrer"
                                style={{ position: 'absolute', inset: 0, zIndex: 10, opacity: 0 }}
                                aria-label={t('deal', 'viewDealAriaLabel', { title: top.title })}
                            />
                        </div>
                    );
                })()}
                <div className="deals-grid">
                    {deals.slice(1, 9).map((car, idx) => (
                        <CarCard key={car.id || car.link || `deal-${idx}`} car={car} index={idx + 1} />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default DealOfTheDay;

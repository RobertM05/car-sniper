import React from 'react';
import PropTypes from 'prop-types';
import { useLanguage } from '../LanguageContext';

const PriceStats = ({ stats, currentSearch }) => {
    const { t } = useLanguage();
    if (!stats) return null;

    const { avg_price, avg_year, avg_km, search_count } = stats;


    const formatPrice = (price) => {
        return new Intl.NumberFormat('ro-RO', {
            style: 'currency',
            currency: 'EUR',
            maximumFractionDigits: 0
        }).format(price);
    };

    return (
        <div className="glass-panel stats-panel">
            <div className="stats-header">
                <h3 className="stats-title">
                    {t('stats', 'title')}: {currentSearch.make} {currentSearch.model}
                </h3>
                <span className="stats-count">
                    {t('stats', 'basedOn', { count: search_count })}
                </span>
            </div>

            <div className="stats-grid">
                <div className="stat-card-item">
                    <div className="stat-card-label">{t('stats', 'avgPrice')}</div>
                    <div className="stat-card-value stat-value-green">
                        {avg_price != null ? formatPrice(avg_price) : 'N/A'}
                    </div>
                </div>

                <div className="stat-card-item">
                    <div className="stat-card-label">{t('stats', 'avgYear')}</div>
                    <div className="stat-card-value stat-value-blue">
                        {avg_year != null ? Math.round(avg_year) : 'N/A'}
                    </div>
                </div>

                <div className="stat-card-item">
                    <div className="stat-card-label">{t('stats', 'avgKm')}</div>
                    <div className="stat-card-value stat-value-pink">
                        {avg_km != null ? `${Math.round(avg_km / 1000)}k` : 'N/A'}
                    </div>
                </div>
            </div>
        </div>
    );
};

PriceStats.propTypes = {
    stats: PropTypes.shape({
        avg_price: PropTypes.number,
        avg_year: PropTypes.number,
        avg_km: PropTypes.number,
        search_count: PropTypes.number,
    }),
    currentSearch: PropTypes.shape({
        make: PropTypes.string,
        model: PropTypes.string,
    }),
};

export default PriceStats;

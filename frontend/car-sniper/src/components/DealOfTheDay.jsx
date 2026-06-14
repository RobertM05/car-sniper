import React, { useState, useEffect } from 'react';
import CarCard from './CarCard';
import SkeletonCard from './SkeletonCard';
import { useLanguage } from '../LanguageContext';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

const DealOfTheDay = () => {
    const { t } = useLanguage();
    const [deals, setDeals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchDeals = async () => {
            try {
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
                <div className="deals-grid">
                    {deals.slice(0, 8).map((car, idx) => (
                        <CarCard key={`deal-${car.id || idx}`} car={car} />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default DealOfTheDay;

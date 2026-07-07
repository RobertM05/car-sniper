import React from 'react';
import { useLanguage } from '../LanguageContext';
import CarCard from './CarCard';

const ResultsList = ({ results }) => {
    const { t } = useLanguage();
    if (!results || results.length === 0) {
        return (
            <div className="empty-state">
                <h3>{t('results', 'noResultsTitle')}</h3>
                <p>{t('results', 'noResultsSubtitle')}</p>
            </div>
        );
    }

    return (
        <div className="results-grid">
            {results.map((car, idx) => (
                <CarCard key={car.id || car.link || idx} car={car} index={idx} />
            ))}
        </div>
    );
};

export default ResultsList;

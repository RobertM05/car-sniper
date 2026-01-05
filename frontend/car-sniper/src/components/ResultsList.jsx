import React from 'react';
import CarCard from './CarCard';

const ResultsList = ({ results }) => {
    if (!results || results.length === 0) {
        return (
            <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '2rem' }}>
                Nu s-au găsit rezultate. Încearcă alți parametri.
            </div>
        );
    }

    return (
        <div className="results-grid">
            {results.map((car, idx) => (
                <CarCard key={`${car.id}-${idx}`} car={car} />
            ))}
        </div>
    );
};

export default ResultsList;

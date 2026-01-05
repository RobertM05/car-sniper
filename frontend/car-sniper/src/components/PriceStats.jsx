import React from 'react';

const PriceStats = ({ stats, currentSearch }) => {
    if (!stats) return null;

    const { avg_price, avg_year, avg_km, search_count } = stats;

    // Format price
    const formatPrice = (price) => {
        return new Intl.NumberFormat('ro-RO', {
            style: 'currency',
            currency: 'EUR',
            maximumFractionDigits: 0
        }).format(price);
    };

    return (
        <div className="glass-panel" style={{
            marginBottom: '2rem',
            padding: '1.5rem',
            background: 'rgba(59, 130, 246, 0.1)', // Light blue tint
            border: '1px solid rgba(59, 130, 246, 0.3)'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--text-primary)' }}>
                    📊 Analiză Piață: {currentSearch.make} {currentSearch.model}
                </h3>
                <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    Bazat pe {search_count} căutări anterioare
                </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
                <div className="stat-item" style={{ textAlign: 'center', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Preț Mediu</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#4ade80' }}>
                        {avg_price ? formatPrice(avg_price) : 'N/A'}
                    </div>
                </div>

                <div className="stat-item" style={{ textAlign: 'center', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>An Mediu</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#60a5fa' }}>
                        {avg_year ? Math.round(avg_year) : 'N/A'}
                    </div>
                </div>

                <div className="stat-item" style={{ textAlign: 'center', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Km Medii</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f472b6' }}>
                        {avg_km ? `${Math.round(avg_km / 1000)}k` : 'N/A'}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PriceStats;

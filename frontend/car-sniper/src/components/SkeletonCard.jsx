import React from 'react';

const SkeletonCard = () => {
    return (
        <div className="glass-panel car-card" style={{ pointerEvents: 'none' }}>
            <div className="car-image-container skeleton" style={{ height: '240px' }}></div>
            <div className="car-content">
                <div className="skeleton" style={{ height: '24px', width: '80%', marginBottom: '1rem' }}></div>
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                    <div className="skeleton" style={{ height: '20px', width: '60px' }}></div>
                    <div className="skeleton" style={{ height: '20px', width: '80px' }}></div>
                    <div className="skeleton" style={{ height: '20px', width: '50px' }}></div>
                </div>
                <div className="car-footer">
                    <div className="skeleton" style={{ height: '32px', width: '120px' }}></div>
                    <div className="skeleton" style={{ height: '20px', width: '80px' }}></div>
                </div>
            </div>
        </div>
    );
};

export default SkeletonCard;

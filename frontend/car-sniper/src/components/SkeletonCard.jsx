import React from 'react';

const SkeletonCard = () => {
    return (
        <div className="skeleton-shell">
            <div className="skeleton-image" />
            <div className="skeleton-content">
                <div className="skeleton-line skeleton-line-title" />
                <div className="skeleton-line skeleton-line-specs" />
                <div className="skeleton-line skeleton-line-price" />
            </div>
            <div className="skeleton-pulse" />
        </div>
    );
};

export default SkeletonCard;

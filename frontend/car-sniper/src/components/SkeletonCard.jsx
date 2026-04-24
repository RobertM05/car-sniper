import React from 'react';

const SkeletonCard = () => {
    return (
        <div className="skeleton-shell">
            <div className="skeleton-core">
                <div className="skeleton-pulse"></div>
            </div>
        </div>
    );
};

export default SkeletonCard;

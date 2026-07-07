import React from 'react';
import PropTypes from 'prop-types';
import { useLanguage } from '../LanguageContext';

const Pagination = ({ carsPerPage, totalCars, paginate, currentPage }) => {
    const { t } = useLanguage();
    const pageNumbers = [];
    const totalPages = Math.ceil(totalCars / carsPerPage);


    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);


    if (currentPage <= 3) {
        endPage = Math.min(5, totalPages);
    }
    if (currentPage > totalPages - 2) {
        startPage = Math.max(1, totalPages - 4);
    }

    for (let i = startPage; i <= endPage; i++) {
        pageNumbers.push(i);
    }

    if (totalCars === 0) return null;

    return (
        <div className="pagination">
            <button
                className="page-btn"
                onClick={() => paginate(currentPage - 1)}
                disabled={currentPage === 1}
            >
                {t('pagination', 'prev')}
            </button>

            {startPage > 1 && (
                <>
                    <button onClick={() => paginate(1)} className="page-btn">1</button>
                    {startPage > 2 && <span style={{ color: 'var(--text-secondary)' }}>...</span>}
                </>
            )}

            {pageNumbers.map(number => (
                <button
                    key={number}
                    onClick={() => paginate(number)}
                    className={`page-btn ${currentPage === number ? 'active' : ''}`}
                >
                    {number}
                </button>
            ))}

            {endPage < totalPages && (
                <>
                    {endPage < totalPages - 1 && <span style={{ color: 'var(--text-secondary)' }}>...</span>}
                    <button onClick={() => paginate(totalPages)} className="page-btn">{totalPages}</button>
                </>
            )}

            <button
                className="page-btn"
                onClick={() => paginate(currentPage + 1)}
                disabled={currentPage === totalPages}
            >
                {t('pagination', 'next')}
            </button>
        </div>
    );
};

Pagination.propTypes = {
    carsPerPage: PropTypes.number.isRequired,
    totalCars: PropTypes.number.isRequired,
    paginate: PropTypes.func.isRequired,
    currentPage: PropTypes.number.isRequired,
};

export default Pagination;

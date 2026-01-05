import React from 'react';

const Pagination = ({ carsPerPage, totalCars, paginate, currentPage }) => {
    const pageNumbers = [];
    const totalPages = Math.ceil(totalCars / carsPerPage);

    // Logic to show limited page numbers (e.g., current - 2 to current + 2)
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    // Adjust if near start or end
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
                ←
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
                →
            </button>
        </div>
    );
};

export default Pagination;

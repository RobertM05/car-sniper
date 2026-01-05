import React, { useState } from 'react';

const AlertModal = ({ isOpen, onClose, onSubmit, searchParams }) => {
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        await onSubmit(email);
        setLoading(false);
        onClose();
    };

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(5px)'
        }}>
            <div className="glass-panel" style={{
                padding: '2rem',
                maxWidth: '400px',
                width: '90%',
                position: 'relative'
            }}>
                <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>🔔 Setează Alertă</h2>

                <div style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
                    Vei primi notificări când apare:
                    <div style={{
                        marginTop: '0.5rem',
                        padding: '0.75rem',
                        background: 'rgba(255,255,255,0.05)',
                        borderRadius: '8px',
                        color: 'var(--primary-color)',
                        fontWeight: '600'
                    }}>
                        {searchParams.make} {searchParams.model}<br />
                        Sub {searchParams.maxPrice || '15000'} €
                    </div>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                        <label>Email-ul tău</label>
                        <input
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="nume@exemplu.com"
                            className="form-control"
                            autoFocus
                        />
                    </div>

                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <button
                            type="button"
                            onClick={onClose}
                            style={{
                                background: 'transparent',
                                border: '1px solid var(--border-color)',
                                color: 'var(--text-secondary)',
                                padding: '0.75rem 1.5rem',
                                borderRadius: '8px',
                                flex: 1
                            }}
                        >
                            Anulează
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="submit-btn"
                            style={{ marginTop: 0, flex: 1 }}
                        >
                            {loading ? "Se salvează..." : "Salvează"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AlertModal;

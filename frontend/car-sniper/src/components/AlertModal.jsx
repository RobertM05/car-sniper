import React, { useState } from 'react';
import { useLanguage } from '../LanguageContext';

const AlertModal = ({ isOpen, onClose, onSubmit, searchParams }) => {
    const { t } = useLanguage();
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
                <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>{t('alert', 'title')}</h2>

                <div style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
                    {t('alert', 'desc')}
                    <div style={{
                        marginTop: '0.5rem',
                        padding: '0.75rem',
                        background: 'rgba(255,255,255,0.05)',
                        borderRadius: '8px',
                        color: 'var(--primary-color)',
                        fontWeight: '600'
                    }}>
                        {searchParams.make} {searchParams.model}<br />
                        {t('alert', 'under')} {searchParams.maxPrice || '15000'} €
                    </div>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                        <label>{t('alert', 'email')}</label>
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
                            {t('alert', 'cancel')}
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="submit-btn"
                            style={{ marginTop: 0, flex: 1 }}
                        >
                            {loading ? t('alert', 'saving') : t('alert', 'save')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AlertModal;

import React, { useState } from 'react';
import { useLanguage } from '../LanguageContext';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');

const AuthModal = ({ isOpen, onClose, onLoginSuccess }) => {
    const { t } = useLanguage();
    const [isLoginMode, setIsLoginMode] = useState(true);
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [status, setStatus] = useState('');
    const [loading, setLoading] = useState(false);

    if (!isOpen) return null;

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setStatus('');

        const endpoint = isLoginMode ? '/api/auth/login' : '/api/auth/register';

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || t('auth', 'errorDefault'));
            }

            if (data.token) {
                localStorage.setItem('jwt_token', data.token);
                localStorage.setItem('user_email', data.email);
                const role = data.role || 'user';
                localStorage.setItem('user_role', role);
            }

            setStatus(t('auth', isLoginMode ? 'loginSuccess' : 'registerSuccess'));
            setTimeout(() => {
                const role = data.role || 'user';
                onLoginSuccess(data.email, data.token, role);
                onClose();
                setStatus('');
                setFormData({ email: '', password: '' });
            }, 1000);

        } catch (err) {
            console.error(err);
            setStatus(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
            backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 9999,
            display: 'flex', justifyContent: 'center', alignItems: 'center'
        }}>
            <div style={{
                background: 'var(--bg-card)', padding: '2.5rem', borderRadius: '12px',
                width: '90%', maxWidth: '400px', border: '1px solid var(--primary-color)',
                boxShadow: '0 0 30px var(--accent-glow)', position: 'relative'
            }}>

                <button onClick={onClose} style={{
                    position: 'absolute', top: '15px', right: '15px', background: 'none', border: 'none',
                    color: 'var(--text-secondary)', fontSize: '24px', cursor: 'pointer'
                }}>×</button>

                <h2 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', textAlign: 'center', fontSize: '1.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    {isLoginMode ? t('auth', 'titleLogin') : t('auth', 'titleRegister')}
                </h2>

                <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', textAlign: 'center', fontSize: '0.9rem' }}>
                    {t('auth', 'subtitle')}
                </p>

                <form onSubmit={handleSubmit} className="modal-form">
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{t('auth', 'emailLabel')}</label>
                        <input type="email" name="email" value={formData.email} onChange={handleChange} required className="form-control" placeholder={t('auth', 'emailPlaceholder')} />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{t('auth', 'passwordLabel')}</label>
                        <input type="password" name="password" value={formData.password} onChange={handleChange} required className="form-control" placeholder={t('auth', 'passwordPlaceholder')} />
                    </div>

                    {status && (
                        <div style={{ marginTop: '0.5rem', textAlign: 'center', fontSize: '14px', color: status === t('auth', 'loginSuccess') || status === t('auth', 'registerSuccess') ? 'var(--primary-color)' : '#ef4444' }}>
                            {status}
                        </div>
                    )}

                    <button type="submit" disabled={loading} className="submit-btn" style={{ marginTop: '1rem', width: '100%' }}>
                        {isLoginMode ? t('auth', 'submitLogin') : t('auth', 'submitRegister')}
                    </button>
                </form>

                <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    {isLoginMode ? t('auth', 'toggleToRegister') : t('auth', 'toggleToLogin')}
                    <button
                        type="button"
                        onClick={() => { setIsLoginMode(!isLoginMode); setStatus(''); }}
                        style={{ background: 'none', border: 'none', color: 'var(--primary-color)', cursor: 'pointer', fontWeight: 'bold', textDecoration: 'underline', marginLeft: '0.25rem' }}
                    >
                        {isLoginMode ? t('auth', 'titleRegister') : t('auth', 'titleLogin')}
                    </button>
                </div>

            </div>
        </div>
    );
};

export default AuthModal;

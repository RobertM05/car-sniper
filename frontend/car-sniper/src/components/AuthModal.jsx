import React, { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');

const AuthModal = ({ isOpen, onClose, onLoginSuccess }) => {
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
        setStatus('Se procesează...');

        const endpoint = isLoginMode ? '/api/auth/login' : '/api/auth/register';

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Eroare de autentificare.");
            }

            setStatus('Succes!');
            setTimeout(() => {
                onLoginSuccess(data.email);
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
                boxShadow: '0 0 30px rgba(0, 243, 255, 0.1)', position: 'relative'
            }}>

                <button onClick={onClose} style={{
                    position: 'absolute', top: '15px', right: '15px', background: 'none', border: 'none',
                    color: 'var(--text-secondary)', fontSize: '24px', cursor: 'pointer'
                }}>×</button>

                <h2 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', textAlign: 'center', fontSize: '1.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    {isLoginMode ? 'Autentificare' : 'Creează Cont'}
                </h2>

                <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', textAlign: 'center', fontSize: '0.9rem' }}>
                    {isLoginMode ? 'Introdu detaliile pentru a accesa contul.' : 'Înregistrează-te pentru a salva alerte.'}
                </p>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Email</label>
                        <input type="email" name="email" value={formData.email} onChange={handleChange} required className="form-control" placeholder="nume@email.com" />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Parolă</label>
                        <input type="password" name="password" value={formData.password} onChange={handleChange} required className="form-control" placeholder="••••••••" />
                    </div>

                    {status && (
                        <div style={{ marginTop: '0.5rem', textAlign: 'center', fontSize: '14px', color: status === 'Succes!' ? 'var(--primary-color)' : '#ef4444' }}>
                            {status}
                        </div>
                    )}

                    <button type="submit" disabled={loading} className="submit-btn" style={{ marginTop: '1rem', width: '100%' }}>
                        {loading ? 'Se procesează...' : (isLoginMode ? 'Intră în cont' : 'Înregistrare')}
                    </button>
                </form>

                <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    {isLoginMode ? 'Nu ai cont? ' : 'Ai deja cont? '}
                    <button
                        type="button"
                        onClick={() => { setIsLoginMode(!isLoginMode); setStatus(''); }}
                        style={{ background: 'none', border: 'none', color: 'var(--primary-color)', cursor: 'pointer', fontWeight: 'bold', textDecoration: 'underline' }}
                    >
                        {isLoginMode ? 'Creează unul' : 'Autentifică-te'}
                    </button>
                </div>

            </div>
        </div>
    );
};

export default AuthModal;

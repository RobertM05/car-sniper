import React, { useState } from 'react';
import { useLanguage } from '../LanguageContext';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');

const ContactModal = ({ isOpen, onClose }) => {
    const { t } = useLanguage();
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        companyEmail: '',
        companyName: '',
        hasWebsite: 'Nu',
        websiteIp: ''
    });
    const [status, setStatus] = useState('');

    if (!isOpen) return null;

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus('');

        try {
            const response = await fetch(`${API_BASE_URL}/api/contact`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: formData.name,
                    phone: formData.phone,
                    company_email: formData.companyEmail,
                    company_name: formData.companyName,
                    has_website: formData.hasWebsite,
                    website_ip: formData.hasWebsite === 'Da' ? formData.websiteIp : null
                })
            });

            if (!response.ok) throw new Error(t('contact', 'error'));

            setStatus(t('contact', 'success'));
            setTimeout(() => {
                onClose();
                setStatus('');
                setFormData({ name: '', phone: '', companyEmail: '', companyName: '', hasWebsite: 'Nu', websiteIp: '' });
            }, 2500);

        } catch (err) {
            console.error(err);
            setStatus(t('contact', 'error'));
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
                width: '90%', maxWidth: '450px', border: '1px solid var(--primary-color)',
                boxShadow: '0 0 30px var(--accent-glow)', position: 'relative'
            }}>

                <button onClick={onClose} style={{
                    position: 'absolute', top: '15px', right: '15px', background: 'none', border: 'none',
                    color: 'var(--text-secondary)', fontSize: '24px', cursor: 'pointer'
                }}>×</button>

                <h2 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', textAlign: 'center', fontSize: '1.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    {t('contact', 'title')}
                </h2>

                <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', textAlign: 'center', fontSize: '0.9rem' }}>
                    {t('contact', 'subtitle')}
                </p>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{t('contact', 'nameLabel')}</label>
                        <input type="text" name="name" value={formData.name} onChange={handleChange} required className="form-control" placeholder={t('contact', 'namePlaceholder')} />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{t('contact', 'phoneLabel')}</label>
                        <input type="tel" name="phone" value={formData.phone} onChange={handleChange} required className="form-control" placeholder={t('contact', 'phonePlaceholder')} />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{t('contact', 'emailLabel')}</label>
                        <input type="email" name="companyEmail" value={formData.companyEmail} onChange={handleChange} required className="form-control" placeholder={t('contact', 'emailPlaceholder')} />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{t('contact', 'companyLabel')}</label>
                        <input type="text" name="companyName" value={formData.companyName} onChange={handleChange} required className="form-control" placeholder={t('contact', 'companyPlaceholder')} />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{t('contact', 'hasWebsite')}</label>
                        <select name="hasWebsite" value={formData.hasWebsite} onChange={handleChange} className="form-control">
                            <option value="Da">Da</option>
                            <option value="Nu">Nu</option>
                        </select>
                    </div>

                    {formData.hasWebsite === 'Da' && (
                        <div className="form-group" style={{ marginBottom: 0 }}>
                            <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{t('contact', 'websiteLabel')}</label>
                            <input type="text" name="websiteIp" value={formData.websiteIp} onChange={handleChange} required className="form-control" placeholder={t('contact', 'websitePlaceholder')} />
                        </div>
                    )}

                    {status && (
                        <div style={{ marginTop: '0.5rem', textAlign: 'center', fontSize: '14px', color: status === t('contact', 'success') ? 'var(--primary-color)' : '#ef4444' }}>
                            {status}
                        </div>
                    )}

                    <button type="submit" className="submit-btn" style={{ marginTop: '1rem', width: '100%' }}>
                        {t('contact', 'submit')}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ContactModal;

import React, { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const ContactModal = ({ isOpen, onClose }) => {
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
        setStatus('Se trimite...');

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

            if (!response.ok) throw new Error("Eroare trimitere.");

            setStatus('Trimis cu succes! Te vom contacta curând.');
            setTimeout(() => {
                onClose();
                setStatus('');
                setFormData({ name: '', phone: '', companyEmail: '', companyName: '', hasWebsite: 'Nu', websiteIp: '' });
            }, 2500);

        } catch (err) {
            console.error(err);
            setStatus('Eroare la trimitere. Încearcă din nou.');
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
                boxShadow: '0 0 30px rgba(0, 243, 255, 0.1)', position: 'relative'
            }}>

                <button onClick={onClose} style={{
                    position: 'absolute', top: '15px', right: '15px', background: 'none', border: 'none',
                    color: 'var(--text-secondary)', fontSize: '24px', cursor: 'pointer'
                }}>×</button>

                <h2 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', textAlign: 'center', fontSize: '1.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    Devino Partener
                </h2>

                <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', textAlign: 'center', fontSize: '0.9rem' }}>
                    Lasă-ne datele tale și vom deschide un cont de dealer pentru tine.
                </p>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Numele Tău</label>
                        <input type="text" name="name" value={formData.name} onChange={handleChange} required className="form-control" placeholder="Ion Popescu" />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Număr de Telefon</label>
                        <input type="tel" name="phone" value={formData.phone} onChange={handleChange} required className="form-control" placeholder="07xx xxx xxx" />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Email Firmă</label>
                        <input type="email" name="companyEmail" value={formData.companyEmail} onChange={handleChange} required className="form-control" placeholder="contact@firma.ro" />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Nume Firmă / Dealer</label>
                        <input type="text" name="companyName" value={formData.companyName} onChange={handleChange} required className="form-control" placeholder="Car Sniper SRL" />
                    </div>

                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Ai deja un website?</label>
                        <select name="hasWebsite" value={formData.hasWebsite} onChange={handleChange} className="form-control">
                            <option value="Da">Da</option>
                            <option value="Nu">Nu</option>
                        </select>
                    </div>

                    {formData.hasWebsite === 'Da' && (
                        <div className="form-group" style={{ marginBottom: 0 }}>
                            <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Website IP</label>
                            <input type="text" name="websiteIp" value={formData.websiteIp} onChange={handleChange} required className="form-control" placeholder="192.168.1.1" />
                        </div>
                    )}

                    {status && (
                        <div style={{ marginTop: '0.5rem', textAlign: 'center', fontSize: '14px', color: status.includes('Eroare') ? '#ef4444' : 'var(--primary-color)' }}>
                            {status}
                        </div>
                    )}

                    <button type="submit" className="submit-btn" style={{ marginTop: '1rem', width: '100%' }}>
                        Trimite Cererea
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ContactModal;

import React, { useState, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { useLanguage } from '../LanguageContext';
import SkeletonCard from './SkeletonCard';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

const AlertManager = () => {
    const { t } = useLanguage();
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const userEmail = localStorage.getItem('user_email');

    const fetchAlerts = () => {
        if (!userEmail) return;
        fetch(API_BASE_URL + '/api/alerts?email=' + encodeURIComponent(userEmail))
            .then(r => r.json())
            .then(d => { setAlerts(d.alerts || []); setLoading(false); })
            .catch(e => { setError(e.message); setLoading(false); });
    };

    useEffect(() => { fetchAlerts(); }, [userEmail]);

    const handleDelete = async (alertId) => {
        try {
            await fetch(API_BASE_URL + '/api/alerts/' + alertId + '?email=' + encodeURIComponent(userEmail), { method: 'DELETE' });
            setAlerts(prev => prev.filter(a => a.id !== alertId));
        } catch (err) {
            console.error('Failed to delete alert:', err);
        }
    };

    const handleToggle = async (alertId, currentStatus) => {
        const newStatus = !currentStatus;
        try {
            const res = await fetch(API_BASE_URL + '/api/alerts/' + alertId + '/toggle?email=' + encodeURIComponent(userEmail), {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ active: newStatus })
            });
            if (res.ok) {
                setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, active: newStatus } : a));
            }
        } catch (err) {
            console.error('Failed to toggle alert:', err);
        }
    };

    if (!userEmail) return <div className="container"><div className="error-message" role="alert">{t('nav', 'account')} required</div></div>;
    if (loading) return <div className="container"><div className="results-grid">{[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}</div></div>;
    if (error) return <div className="container"><div className="error-message" role="alert">{error}</div></div>;

    return (
        <div className="container">
            <Helmet><title>{t('alerts', 'title')} | Motorbit</title><meta name="description" content="Manage your Motorbit price alerts. Get notified when new cars match your criteria." /></Helmet>
            <h1 style={{ marginBottom: '2rem', color: 'var(--text-primary)', fontSize: '1.75rem', fontWeight: 700 }}>{t('alerts', 'title')}</h1>
            {alerts.length === 0 ? (
                <div className="empty-state">
                    <h3>{t('alerts', 'noAlerts')}</h3>
                    <p>{t('alerts', 'noAlertsDesc')}</p>
                </div>
            ) : (
                <div className="alerts-table-wrap">
                    <table className="alerts-table">
                        <thead>
                            <tr>
                                <th>Status</th>
                                <th>{t('search', 'make')}</th>
                                <th>{t('search', 'model')}</th>
                                <th>{t('search', 'maxPrice')}</th>
                                <th>{t('alerts', 'created')}</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {alerts.map(alert => (
                                <tr key={alert.id} style={{ opacity: alert.active ? 1 : 0.6 }}>
                                    <td>
                                        <span style={{
                                            padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 'bold',
                                            backgroundColor: alert.active ? 'rgba(16, 185, 129, 0.2)' : 'rgba(107, 114, 128, 0.2)',
                                            color: alert.active ? '#10b981' : '#9ca3af'
                                        }}>
                                            {alert.active ? 'Active' : 'Paused'}
                                        </span>
                                    </td>
                                    <td>{alert.make}</td>
                                    <td>{alert.model}</td>
                                    <td>{alert.max_price ? alert.max_price + ' EUR' : '-'}</td>
                                    <td>{alert.created_at ? new Date(alert.created_at).toLocaleDateString() : '-'}</td>
                                    <td>
                                        <div style={{ display: 'flex', gap: '8px' }}>
                                            <button className="secondary-btn" style={{ padding: '6px 12px', fontSize: '0.85rem' }} onClick={() => handleToggle(alert.id, alert.active)}>
                                                {alert.active ? 'Pause' : 'Resume'}
                                            </button>
                                            <button className="inventory-delete-btn" onClick={() => handleDelete(alert.id)}>{t('alerts', 'delete')}</button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default AlertManager;

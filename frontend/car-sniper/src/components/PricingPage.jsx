import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Check } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

const tiers = [
    {
        name: 'Free',
        price: '0',
        period: 'forever',
        listings: '5',
        features: ['5 active listings', 'Basic dealer profile', 'Standard support'],
        tier: 'free',
        cta: 'Current Plan',
        featured: false,
    },
    {
        name: 'Premium',
        price: '50',
        period: 'month',
        listings: '50',
        features: ['50 active listings', 'Listing performance analytics', 'Verified Partner badge', 'Priority email support'],
        tier: 'premium',
        cta: 'Subscribe',
        featured: true,
    },
    {
        name: 'Enterprise',
        price: '200',
        period: 'month',
        listings: 'Unlimited',
        features: ['Unlimited listings', 'Advanced analytics', 'API sync access', 'Bulk CSV upload', 'Priority placement', 'Dedicated support'],
        tier: 'enterprise',
        cta: 'Subscribe',
        featured: false,
    },
];

const PricingPage = () => {
    const userEmail = localStorage.getItem('user_email');

    const handleSubscribe = async (tier) => {
        if (!userEmail) {
            alert('Please log in first.');
            return;
        }
        if (tier === 'free') return;
        try {
            const res = await fetch(API_BASE_URL + '/api/stripe/create-checkout?email=' + encodeURIComponent(userEmail), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tier }),
            });
            const data = await res.json();
            if (data.url) window.location.href = data.url;
        } catch (err) {
            console.error('Checkout error:', err);
        }
    };

    return (
        <div className="container" style={{ paddingTop: '6rem' }}>
            <Helmet><title>Pricing | CarSniper</title></Helmet>
            <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Dealer Plans</h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.125rem' }}>Choose the plan that fits your dealership.</p>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', maxWidth: '960px', margin: '0 auto' }}>
                {tiers.map(tier => (
                    <div key={tier.name} style={{
                        border: tier.featured ? '2px solid var(--primary-color)' : '1px solid var(--border-shell)',
                        borderRadius: '1rem',
                        padding: '2rem',
                        background: 'var(--bg-primary)',
                        position: 'relative',
                    }}>
                        {tier.featured && (
                            <div style={{
                                position: 'absolute', top: '-12px', left: '50%', transform: 'translateX(-50%)',
                                background: 'var(--primary-color)', color: '#fff', padding: '0.25rem 1rem',
                                borderRadius: '100px', fontSize: '0.75rem', fontWeight: 700,
                            }}>Most Popular</div>
                        )}
                        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>{tier.name}</h2>
                        <div style={{ marginBottom: '1.5rem' }}>
                            <span style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-primary)' }}>{tier.price} EUR</span>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>/{tier.period}</span>
                        </div>
                        <ul style={{ listStyle: 'none', padding: 0, marginBottom: '2rem' }}>
                            {tier.features.map(f => (
                                <li key={f} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 0', color: 'var(--text-secondary)', fontSize: '0.9375rem' }}>
                                    <Check size={16} color="var(--primary-color)" /> {f}
                                </li>
                            ))}
                        </ul>
                        <button
                            className={tier.featured ? 'submit-btn' : 'secondary-btn'}
                            style={{ width: '100%' }}
                            onClick={() => handleSubscribe(tier.tier)}
                        >
                            {tier.cta}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PricingPage;

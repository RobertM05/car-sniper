import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import CarCard from './CarCard';
import SkeletonCard from './SkeletonCard';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

const DealerProfile = () => {
    const { email } = useParams();
    const [profile, setProfile] = useState(null);
    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchDealer = async () => {
            try {
                setLoading(true);
                const res = await fetch(`${API_BASE_URL}/api/dealer/listings?email=${encodeURIComponent(email)}`);
                if (!res.ok) throw new Error('Dealer not found');
                const data = await res.json();
                setProfile(data.profile || null);
                setListings(data.listings || []);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchDealer();
    }, [email]);

    if (loading) {
        return (
            <div className="container">
                <div className="results-grid">
                    {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container">
                <div className="error-message" role="alert">Dealer not found.</div>
            </div>
        );
    }

    return (
        <div className="container">
            <Helmet>
                <title>{profile?.company_name || email} | CarSniper</title>
            </Helmet>
            <div className="dealer-header">
                <h1>{profile?.company_name || email}</h1>
                {profile?.phone && <p className="dealer-contact">{profile.phone}</p>}
                {profile?.website && (
                    <a href={profile.website} target="_blank" rel="noreferrer" className="dealer-website">
                        {profile.website}
                    </a>
                )}
                <p className="dealer-listing-count">{listings.length} active listings</p>
            </div>
            {listings.length > 0 ? (
                <div className="results-grid">
                    {listings.map((car, idx) => (
                        <CarCard key={car.id || idx} car={car} index={idx} />
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    <h3>No listings yet</h3>
                    <p>This dealer hasn't added any inventory.</p>
                </div>
            )}
        </div>
    );
};

export default DealerProfile;

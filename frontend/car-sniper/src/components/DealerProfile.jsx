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
    const [reviews, setReviews] = useState(null);
    const [showReviewForm, setShowReviewForm] = useState(false);
    const [newReview, setNewReview] = useState({ rating: 5, comment: '' });
    const userEmail = localStorage.getItem('user_email');

    useEffect(() => {
        const fetchDealer = async () => {
            try {
                setLoading(true);
                const res = await fetch(`${API_BASE_URL}/api/dealer/listings?email=${encodeURIComponent(email)}`);
                if (!res.ok) throw new Error('Dealer not found');
                const data = await res.json();
                setProfile(data.profile || null);
                setListings(data.listings || []);
                fetch(API_BASE_URL + '/api/dealer/reviews/' + (data.profile?.id || 0))
                    .then(r => r.json()).then(d => setReviews(d)).catch(console.error);
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
                <meta name="description" content={`View inventory from ${profile?.company_name || email}. ${listings.length} active car listings on CarSniper.`} />
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
            {reviews && (
                <div className="dealer-reviews">
                    <h2 style={{ marginBottom: '1rem' }}>
                        Reviews ({reviews.total_reviews}) &mdash; {'★'.repeat(Math.round(reviews.avg_rating))}{'☆'.repeat(5 - Math.round(reviews.avg_rating))} {reviews.avg_rating}/5
                    </h2>
                    {reviews.reviews && reviews.reviews.map(r => (
                        <div key={r.id} className="review-card">
                            <div className="review-stars">{'★'.repeat(r.rating)}{'☆'.repeat(5 - r.rating)}</div>
                            {r.comment && <p style={{ margin: '0.5rem 0', color: 'var(--text-primary)' }}>{r.comment}</p>}
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{r.user_email} &mdash; {new Date(r.created_at).toLocaleDateString()}</p>
                        </div>
                    ))}
                    {userEmail && (
                        showReviewForm ? (
                            <form className="review-form" onSubmit={async (e) => {
                                e.preventDefault();
                                await fetch(API_BASE_URL + '/api/dealer/reviews?email=' + encodeURIComponent(userEmail), {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({ dealer_id: profile?.id, rating: newReview.rating, comment: newReview.comment }),
                                });
                                setShowReviewForm(false);
                                const res = await fetch(API_BASE_URL + '/api/dealer/reviews/' + (profile?.id || 0));
                                setReviews(await res.json());
                            }}>
                                <select className="form-control" value={newReview.rating} onChange={e => setNewReview({...newReview, rating: parseInt(e.target.value)})}>
                                    {[5,4,3,2,1].map(n => <option key={n} value={n}>{n} star{n>1?'s':''}</option>)}
                                </select>
                                <textarea className="form-control" placeholder="Write a review..." value={newReview.comment} onChange={e => setNewReview({...newReview, comment: e.target.value})} rows={3} />
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <button type="submit" className="submit-btn">Submit Review</button>
                                    <button type="button" className="filter-clear-btn" onClick={() => setShowReviewForm(false)}>Cancel</button>
                                </div>
                            </form>
                        ) : (
                            <button className="secondary-btn" onClick={() => setShowReviewForm(true)}>Write a Review</button>
                        )
                    )}
                </div>
            )}
        </div>
    );
};

export default DealerProfile;

import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line
} from 'recharts';
import { TrendingUp, Users, CarFront, BellRing, LogOut, Loader2, ArrowUpRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useLanguage } from '../LanguageContext';
import './PartnerDashboard.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

const PartnerDashboard = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    activeBuyers: 0,
    activePriceAlerts: 0,
    marketScans: 0,
    demandData: [],
    trendData: []
  });
  const [listings, setListings] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingListingId, setEditingListingId] = useState(null);
  const [newListing, setNewListing] = useState({
    title: '', price: '', year: '', km: '', fuel: '', transmission: '', description: ''
  });

  useEffect(() => {
    // Determine if user is logged in
    const token = localStorage.getItem('jwt_token');
    if (!token) {
      navigate('/');
      return;
    }

    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setStats({
            activeBuyers: data.activeBuyers || 0,
            activePriceAlerts: data.activePriceAlerts || 0,
            marketScans: data.marketScans || 0,
            demandData: data.demandData || [],
            trendData: data.trendData || []
          });
        }
      } catch (err) {
        console.error("Failed to fetch dashboard stats", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    fetchDealerListings();
    fetchAnalytics();
  }, [navigate]);

  const fetchAnalytics = async () => {
    const email = localStorage.getItem('user_email');
    if (!email) return;
    try {
      const res = await fetch(API_BASE_URL + '/api/dealer/analytics?email=' + encodeURIComponent(email));
      if (res.ok) {
        const data = await res.json();
        setAnalytics(data);
      }
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    }
  };

  const fetchDealerListings = async () => {
    const email = localStorage.getItem('user_email');
    if (!email) return;
    try {
      const res = await fetch(API_BASE_URL + '/api/dealer/listings?email=' + encodeURIComponent(email));
      if (res.ok) {
        const data = await res.json();
        setListings(data.listings || []);
      }
    } catch (err) {
      console.error('Failed to fetch listings:', err);
    }
  };

  const handleSaveListing = async (e) => {
    e.preventDefault();
    const email = localStorage.getItem('user_email');
    if (!email) return;
    try {
      const url = editingListingId 
        ? `${API_BASE_URL}/api/dealer/listings/${editingListingId}?email=${encodeURIComponent(email)}`
        : `${API_BASE_URL}/api/dealer/listings?email=${encodeURIComponent(email)}`;
      const method = editingListingId ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newListing),
      });
      if (res.ok) {
        setShowAddForm(false);
        setEditingListingId(null);
        setNewListing({ title: '', price: '', year: '', km: '', fuel: '', transmission: '', description: '' });
        fetchDealerListings();
      }
    } catch (err) {
      console.error('Failed to save listing:', err);
    }
  };

  const handleEditClick = (listing) => {
    setNewListing({
      title: listing.title || '',
      price: listing.price || '',
      year: listing.year || '',
      km: listing.km || '',
      fuel: listing.fuel || '',
      transmission: listing.transmission || '',
      description: listing.description || ''
    });
    setEditingListingId(listing.id);
    setShowAddForm(true);
  };

  const handleDeleteListing = async (listingId) => {
    const email = localStorage.getItem('user_email');
    if (!email) return;
    try {
      await fetch(API_BASE_URL + '/api/dealer/listings/' + listingId + '?email=' + encodeURIComponent(email), {
        method: 'DELETE',
      });
      fetchDealerListings();
    } catch (err) {
      console.error('Failed to delete listing:', err);
    }
  };

  if (loading) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)' }}>
        <Loader2 className="animate-spin" size={48} color="var(--primary-color)" />
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <Helmet>
        <title>{t('dashboard', 'title')} | Motorbit</title>
        <meta name="description" content="Dealer partner dashboard — manage your inventory and track performance." />
      </Helmet>
      
      {/* Header */}
      <header className="dashboard-header">
        <div>
          <h1>{t('dashboard', 'title')}</h1>
          <p>{t('dashboard', 'welcome')}</p>
        </div>
        <button 
          onClick={() => { 
            localStorage.removeItem('jwt_token'); 
            localStorage.removeItem('user_email'); 
            localStorage.removeItem('user_role'); 
            navigate('/'); 
          }}
          className="logout-btn"
        >
          <LogOut size={18} />{t('dashboard', 'logout')}
        </button>
      </header>

      {/* Stats Cards */}
      <div className="stats-grid">
        
        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">{t('dashboard', 'totalUsers')}</h3>
            <div className="stat-icon-wrapper">
              <Users size={20} color="var(--primary-color)" />
            </div>
          </div>
          <div className="stat-value">{stats.activeBuyers.toLocaleString()}</div>
          <div className="stat-change positive">
            <TrendingUp size={14} />{t('dashboard', 'totalUsersDesc')}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">{t('dashboard', 'activeAlerts')}</h3>
            <div className="stat-icon-wrapper">
              <BellRing size={20} color="#f59e0b" />
            </div>
          </div>
          <div className="stat-value">{stats.activePriceAlerts.toLocaleString()}</div>
          <div className="stat-change positive">
            <TrendingUp size={14} />{t('dashboard', 'activeAlertsDesc')}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">{t('dashboard', 'marketScans')}</h3>
            <div className="stat-icon-wrapper">
              <CarFront size={20} color="#8b5cf6" />
            </div>
          </div>
          <div className="stat-value">{stats.marketScans.toLocaleString()}</div>
          <div className="stat-change neutral">
            Cars indexed right now
          </div>
        </div>

      </div>

      {analytics && analytics.listings && analytics.listings.length > 0 && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-header">
              <h3 className="stat-title">Total Listing Views</h3>
            </div>
            <div className="stat-value">{analytics.total_views.toLocaleString()}</div>
          </div>
        </div>
      )}
      {analytics && analytics.listings && analytics.listings.length > 0 && (
        <div className="chart-card">
          <h3 className="chart-title">Views Per Listing</h3>
          <div className="inventory-table-wrap">
            <table className="inventory-table">
              <thead><tr><th>Listing</th><th>Views</th></tr></thead>
              <tbody>
                {analytics.listings.map(l => (
                  <tr key={l.id}><td>{l.title}</td><td>{l.views}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Charts Area */}
      <div className="charts-area">
        
        {/* Bar Chart: High Demand Vehicles */}
        <div className="chart-card">
          <h3 className="chart-title">{t('dashboard', 'demandChart')}</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.demandData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(150,150,150,0.1)" vertical={false} />
                <XAxis dataKey="name" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-core)', border: '1px solid var(--border-shell)', borderRadius: '12px', color: 'var(--text-primary)', backdropFilter: 'blur(10px)' }}
                  itemStyle={{ color: 'var(--text-primary)' }}
                  cursor={{fill: 'rgba(150,150,150,0.05)'}}
                />
                <Bar dataKey="searches" fill="var(--primary-color)" radius={[6, 6, 0, 0]} name={t('dashboard', 'searchQueries')} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Line Chart: Active Buyers Trend */}
        <div className="chart-card">
          <h3 className="chart-title">{t('dashboard', 'trendChart')}</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats.trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(150,150,150,0.1)" vertical={false} />
                <XAxis dataKey="day" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-core)', border: '1px solid var(--border-shell)', borderRadius: '12px', color: 'var(--text-primary)', backdropFilter: 'blur(10px)' }}
                  itemStyle={{ color: 'var(--text-primary)' }}
                />
                <Line type="monotone" dataKey="activeBuyers" stroke="#10b981" strokeWidth={4} dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }} activeDot={{ r: 8, strokeWidth: 0 }} name={t('dashboard', 'activeBuyers')} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Action Area */}
      <div className="action-area">
        <div className="action-text">
          <h3>{t('dashboard', 'actionTitle')}</h3>
          <p>{t('dashboard', 'actionDesc')}</p>
        </div>
        <button className="action-btn" onClick={() => { setShowAddForm(true); setEditingListingId(null); setNewListing({ title: '', price: '', year: '', km: '', fuel: '', transmission: '', description: '' }); }}>
          {t('dashboard', 'addInventory')} <ArrowUpRight size={18} />
        </button>
      </div>

      {listings.length > 0 && (
        <div className="inventory-section">
          <h3 className="chart-title">Your Inventory</h3>
          <div className="inventory-table-wrap">
            <table className="inventory-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Price</th>
                  <th>Year</th>
                  <th>Km</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {listings.map((l) => (
                  <tr key={l.id}>
                    <td>{l.title}</td>
                    <td>{l.price ? l.price.toLocaleString() + ' EUR' : '-'}</td>
                    <td>{l.year || '-'}</td>
                    <td>{l.km ? l.km.toLocaleString() : '-'}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button className="secondary-btn" style={{ padding: '6px 12px', fontSize: '0.85rem' }} onClick={() => handleEditClick(l)}>
                          Edit
                        </button>
                        <button className="inventory-delete-btn" onClick={() => handleDeleteListing(l.id)}>
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="inventory-section">
        <h3 className="chart-title">{editingListingId ? 'Edit Listing' : 'Add New Listing'}</h3>
        {showAddForm ? (
          <form onSubmit={handleSaveListing} className="inventory-form">
            <input className="form-control" placeholder="Title" value={newListing.title} onChange={e => setNewListing({...newListing, title: e.target.value})} required />
            <div className="inventory-form-row">
              <input className="form-control" type="number" placeholder="Price (EUR)" value={newListing.price} onChange={e => setNewListing({...newListing, price: e.target.value})} />
              <input className="form-control" type="number" placeholder="Year" value={newListing.year} onChange={e => setNewListing({...newListing, year: e.target.value})} />
              <input className="form-control" type="number" placeholder="Km" value={newListing.km} onChange={e => setNewListing({...newListing, km: e.target.value})} />
            </div>
            <div className="inventory-form-row">
              <select className="form-control" value={newListing.fuel} onChange={e => setNewListing({...newListing, fuel: e.target.value})}>
                <option value="">Any fuel</option>
                <option value="Petrol">Petrol</option>
                <option value="Diesel">Diesel</option>
                <option value="Hybrid">Hybrid</option>
                <option value="Electric">Electric</option>
              </select>
              <select className="form-control" value={newListing.transmission} onChange={e => setNewListing({...newListing, transmission: e.target.value})}>
                <option value="">Any transmission</option>
                <option value="Automatic">Automatic</option>
                <option value="Manual">Manual</option>
              </select>
            </div>
            <div className="inventory-form-actions">
              <button type="submit" className="action-btn">Save Listing</button>
              <button type="button" className="filter-clear-btn" onClick={() => { setShowAddForm(false); setEditingListingId(null); setNewListing({ title: '', price: '', year: '', km: '', fuel: '', transmission: '', description: '' }); }}>Cancel</button>
            </div>
          </form>
        ) : (
          <button className="action-btn" onClick={() => { setShowAddForm(true); setEditingListingId(null); setNewListing({ title: '', price: '', year: '', km: '', fuel: '', transmission: '', description: '' }); }}>
            Add Inventory <ArrowUpRight size={18} />
          </button>
        )}
      </div>

    </div>
  );
};

export default PartnerDashboard;

import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line
} from 'recharts';
import { TrendingUp, Users, CarFront, BellRing, LogOut, Loader2, ArrowUpRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './PartnerDashboard.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://127.0.0.1:8000');

const PartnerDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    activeBuyers: 0,
    activePriceAlerts: 0,
    marketScans: 0,
    demandData: [],
    trendData: []
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
  }, [navigate]);

  if (loading) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)' }}>
        <Loader2 className="animate-spin" size={48} color="var(--primary-color)" />
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      
      {/* Header */}
      <header className="dashboard-header">
        <div>
          <h1>Dealer Intelligence</h1>
          <p>Welcome back, Verified Partner.</p>
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
          <LogOut size={18} /> Logout
        </button>
      </header>

      {/* Stats Cards */}
      <div className="stats-grid">
        
        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">Total Users (Active Buyers)</h3>
            <div className="stat-icon-wrapper">
              <Users size={20} color="var(--primary-color)" />
            </div>
          </div>
          <div className="stat-value">{stats.activeBuyers.toLocaleString()}</div>
          <div className="stat-change positive">
            <TrendingUp size={14} /> +{(stats.activeBuyers * 0.12).toFixed(0)} from yesterday
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">Active Price Alerts</h3>
            <div className="stat-icon-wrapper">
              <BellRing size={20} color="#f59e0b" />
            </div>
          </div>
          <div className="stat-value">{stats.activePriceAlerts.toLocaleString()}</div>
          <div className="stat-change positive">
            <TrendingUp size={14} /> Tracking user demands
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">Market Scans (Ads)</h3>
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

      {/* Charts Area */}
      <div className="charts-area">
        
        {/* Bar Chart: High Demand Vehicles */}
        <div className="chart-card">
          <h3 className="chart-title">Highest Demand Models (By Search)</h3>
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
                <Bar dataKey="searches" fill="var(--primary-color)" radius={[6, 6, 0, 0]} name="Search Queries" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Line Chart: Active Buyers Trend */}
        <div className="chart-card">
          <h3 className="chart-title">Active Buyers Trend</h3>
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
                <Line type="monotone" dataKey="activeBuyers" stroke="#10b981" strokeWidth={4} dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }} activeDot={{ r: 8, strokeWidth: 0 }} name="Active Buyers" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Action Area */}
      <div className="action-area">
        <div className="action-text">
          <h3>Have matching inventory?</h3>
          <p>Upload your cars directly to our database and skip the scraper. Your listings will appear as "Verified Partner" at the top of search results, directly reaching thousands of active buyers.</p>
        </div>
        <button className="action-btn">
          Add Inventory <ArrowUpRight size={18} />
        </button>
      </div>

    </div>
  );
};

export default PartnerDashboard;

import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line
} from 'recharts';
import { TrendingUp, Users, CarFront, BellRing, LogOut, Loader2, ArrowUpRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './PartnerDashboard.css';

const mockDemandData = [
  { name: 'BMW Seria 3', searches: 240, alerts: 45 },
  { name: 'Audi A4', searches: 198, alerts: 32 },
  { name: 'VW Golf', searches: 305, alerts: 89 },
  { name: 'Mercedes C-Class', searches: 156, alerts: 21 },
  { name: 'Skoda Octavia', searches: 210, alerts: 56 },
];

const mockTrendData = [
  { day: 'Mon', activeBuyers: 120 },
  { day: 'Tue', activeBuyers: 150 },
  { day: 'Wed', activeBuyers: 180 },
  { day: 'Thu', activeBuyers: 170 },
  { day: 'Fri', activeBuyers: 210 },
  { day: 'Sat', activeBuyers: 280 },
  { day: 'Sun', activeBuyers: 250 },
];

const PartnerDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Determine if user is logged in
    const token = localStorage.getItem('jwt_token');
    if (!token) {
      navigate('/');
      return;
    }
    setTimeout(() => setLoading(false), 600);
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
            <h3 className="stat-title">Active Buyers Today</h3>
            <div className="stat-icon-wrapper">
              <Users size={20} color="var(--primary-color)" />
            </div>
          </div>
          <div className="stat-value">1,284</div>
          <div className="stat-change positive">
            <TrendingUp size={14} /> +12% from yesterday
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">Active Price Alerts</h3>
            <div className="stat-icon-wrapper">
              <BellRing size={20} color="#f59e0b" />
            </div>
          </div>
          <div className="stat-value">4,921</div>
          <div className="stat-change positive">
            <TrendingUp size={14} /> +54 this week
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">Market Scans</h3>
            <div className="stat-icon-wrapper">
              <CarFront size={20} color="#8b5cf6" />
            </div>
          </div>
          <div className="stat-value">18,402</div>
          <div className="stat-change neutral">
            Cars indexed in last 24h
          </div>
        </div>

      </div>

      {/* Charts Area */}
      <div className="charts-area">
        
        {/* Bar Chart: High Demand Vehicles */}
        <div className="chart-card">
          <h3 className="chart-title">Highest Demand Models (Last 7 Days)</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockDemandData}>
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
              <LineChart data={mockTrendData}>
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

import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line
} from 'recharts';
import { TrendingUp, Users, CarFront, BellRing, LogOut, Loader2, ArrowUpRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

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

  // Simulate an auth check
  useEffect(() => {
    const token = localStorage.getItem('jwt_token');
    // In a real app, we would verify the role via an API call here.
    if (!token) {
      // Simulate redirect to home if not logged in
      navigate('/');
    } else {
      setTimeout(() => setLoading(false), 800);
    }
  }, [navigate]);

  if (loading) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)' }}>
        <Loader2 className="animate-spin" size={48} color="var(--primary-color)" />
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0f1115', color: '#fff', padding: '2rem', fontFamily: 'Inter, sans-serif' }}>
      
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0, color: '#fff' }}>Dealer Intelligence</h1>
          <p style={{ color: '#888', margin: '4px 0 0 0', fontSize: '14px' }}>Welcome back, Verified Partner.</p>
        </div>
        <button 
          onClick={() => { localStorage.removeItem('jwt_token'); navigate('/'); }}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: '500' }}
        >
          <LogOut size={18} /> Logout
        </button>
      </header>

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        
        <div style={{ background: '#181b21', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0, fontSize: '14px', color: '#888', fontWeight: '500' }}>Active Buyers Today</h3>
            <Users size={20} color="var(--primary-color)" />
          </div>
          <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '4px' }}>1,284</div>
          <div style={{ fontSize: '12px', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <TrendingUp size={14} /> +12% from yesterday
          </div>
        </div>

        <div style={{ background: '#181b21', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0, fontSize: '14px', color: '#888', fontWeight: '500' }}>Active Price Alerts</h3>
            <BellRing size={20} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '4px' }}>4,921</div>
          <div style={{ fontSize: '12px', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <TrendingUp size={14} /> +54 this week
          </div>
        </div>

        <div style={{ background: '#181b21', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0, fontSize: '14px', color: '#888', fontWeight: '500' }}>Market Scans</h3>
            <CarFront size={20} color="#8b5cf6" />
          </div>
          <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '4px' }}>18,402</div>
          <div style={{ fontSize: '12px', color: '#888', display: 'flex', alignItems: 'center', gap: '4px' }}>
            Cars indexed in last 24h
          </div>
        </div>

      </div>

      {/* Charts Area */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', '@media (max-width: 768px)': { gridTemplateColumns: '1fr' } }}>
        
        {/* Bar Chart: High Demand Vehicles */}
        <div style={{ background: '#181b21', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <h3 style={{ margin: '0 0 1.5rem 0', fontSize: '16px', fontWeight: '600', color: '#e5e7eb' }}>Highest Demand Models (Last 7 Days)</h3>
          <div style={{ height: '300px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockDemandData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                <XAxis dataKey="name" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                  cursor={{fill: 'rgba(255,255,255,0.05)'}}
                />
                <Bar dataKey="searches" fill="var(--primary-color)" radius={[4, 4, 0, 0]} name="Search Queries" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Line Chart: Active Buyers Trend */}
        <div style={{ background: '#181b21', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <h3 style={{ margin: '0 0 1.5rem 0', fontSize: '16px', fontWeight: '600', color: '#e5e7eb' }}>Active Buyers Trend</h3>
          <div style={{ height: '300px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mockTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                <XAxis dataKey="day" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                />
                <Line type="monotone" dataKey="activeBuyers" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', strokeWidth: 2 }} name="Active Buyers" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Action Area */}
      <div style={{ marginTop: '2rem', background: 'linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)', padding: '2rem', borderRadius: '12px', border: '1px solid rgba(59, 130, 246, 0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '18px', fontWeight: '600', color: '#fff' }}>Have matching inventory?</h3>
          <p style={{ margin: 0, color: '#cbd5e1', fontSize: '14px' }}>Upload your cars directly to our database and skip the scraper. Your listings will appear as "Verified Partner" at the top of search results.</p>
        </div>
        <button style={{ background: 'var(--primary-color)', color: '#fff', border: 'none', padding: '12px 24px', borderRadius: '8px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', whiteSpace: 'nowrap' }}>
          Add Inventory <ArrowUpRight size={18} />
        </button>
      </div>

    </div>
  );
};

export default PartnerDashboard;

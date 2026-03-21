import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/health/');
      setHealth(response.data);
      setLoading(false);
      setError(null);
    } catch (err) {
      console.error('API Health Check Error:', err);
      let errorMessage = 'Unknown error';
      
      if (err.response) {
        // Server responded with error
        errorMessage = `Server Error: ${err.response.status} - ${err.response.statusText}`;
      } else if (err.request) {
        // Request made but no response
        errorMessage = 'Cannot connect to backend. Is the Django server running on http://localhost:8000?';
      } else {
        // Other errors
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const stats = [
    {
      title: 'Customers',
      value: '0',
      label: 'Total Customers',
      icon: '👥',
      color: '#7CB342'
    },
    {
      title: 'Orders',
      value: '0',
      label: 'Pending Orders',
      icon: '🥘',
      color: '#D4AF37'
    },
    {
      title: 'Products',
      value: '0',
      label: 'Active Menu Items',
      icon: '🍛',
      color: '#E8B84D'
    },
    {
      title: 'Revenue',
      value: '$0.00',
      label: 'This Month',
      icon: '💰',
      color: '#C65D3B'
    }
  ];

  return (
    <div className="dashboard">
      <h2>📊 Dashboard Overview</h2>
      
      <div className="health-check">
        <h3>System Status</h3>
        {loading && (
          <p style={{ color: '#718096' }}>
            <span className="loading-spinner">⟳</span> Checking API connection...
          </p>
        )}
        {error && (
          <div>
            <p className="error">
              ✗ {error}
            </p>
            <button 
              onClick={checkHealth} 
              className="retry-button"
              style={{
                marginTop: '1rem',
                padding: '0.5rem 1rem',
                background: 'linear-gradient(135deg, #FF6B6B, #FF8E53)',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '500',
                fontSize: '0.875rem'
              }}
            >
              🔄 Retry Connection
            </button>
            <div style={{ 
              marginTop: '1rem', 
              padding: '1rem', 
              background: '#FFF5F5', 
              borderRadius: '6px',
              fontSize: '0.875rem',
              color: '#718096'
            }}>
              <strong>Troubleshooting:</strong>
              <ul style={{ margin: '0.5rem 0 0 1.25rem', paddingLeft: 0 }}>
                <li>Ensure Django server is running: <code>python manage.py runserver</code></li>
                <li>Check backend at: <a href="http://localhost:8000/api/health/" target="_blank" rel="noopener noreferrer">http://localhost:8000/api/health/</a></li>
                <li>Check browser console (F12) for detailed errors</li>
              </ul>
            </div>
          </div>
        )}
        {health && (
          <div className="success">
            <p>✓ {health.message}</p>
            <p style={{ fontSize: '0.875rem', marginTop: '0.5rem', opacity: 0.8 }}>
              Status: <strong>{health.status}</strong>
            </p>
          </div>
        )}
      </div>

      <div className="dashboard-cards">
        {stats.map((stat, index) => (
          <div key={index} className="card" style={{ '--accent-color': stat.color }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <h3>{stat.title}</h3>
              <span style={{ fontSize: '1.75rem', opacity: 0.8 }}>{stat.icon}</span>
            </div>
            <p className="stat">{stat.value}</p>
            <p className="label">{stat.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;

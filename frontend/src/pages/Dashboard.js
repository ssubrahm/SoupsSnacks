import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await api.get('/health/');
        setHealth(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };
    
    checkHealth();
  }, []);

  const stats = [
    {
      title: 'Customers',
      value: '0',
      label: 'Total Customers',
      icon: '👥',
      color: '#FF6B6B'
    },
    {
      title: 'Orders',
      value: '0',
      label: 'Pending Orders',
      icon: '📦',
      color: '#4ECDC4'
    },
    {
      title: 'Products',
      value: '0',
      label: 'Active Products',
      icon: '🍲',
      color: '#95E1D3'
    },
    {
      title: 'Revenue',
      value: '$0.00',
      label: 'This Month',
      icon: '💰',
      color: '#FFE66D'
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
          <p className="error">
            ✗ Connection Error: {error}
          </p>
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

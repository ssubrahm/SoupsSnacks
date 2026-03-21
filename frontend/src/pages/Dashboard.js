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

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      
      <div className="health-check">
        <h3>API Status</h3>
        {loading && <p>Checking API connection...</p>}
        {error && <p className="error">Error: {error}</p>}
        {health && (
          <div className="success">
            <p>✓ {health.message}</p>
            <p>Status: {health.status}</p>
          </div>
        )}
      </div>

      <div className="dashboard-cards">
        <div className="card">
          <h3>Customers</h3>
          <p className="stat">0</p>
          <p className="label">Total Customers</p>
        </div>
        
        <div className="card">
          <h3>Orders</h3>
          <p className="stat">0</p>
          <p className="label">Pending Orders</p>
        </div>
        
        <div className="card">
          <h3>Products</h3>
          <p className="stat">0</p>
          <p className="label">Active Products</p>
        </div>
        
        <div className="card">
          <h3>Revenue</h3>
          <p className="stat">$0.00</p>
          <p className="label">This Month</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import './Customers.css';

const Customers = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [filterActive, setFilterActive] = useState('all');
  const [stats, setStats] = useState({ total: 0, active: 0, inactive: 0 });

  useEffect(() => {
    fetchCustomers();
    fetchStats();
  }, [search, filterActive]);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const params = {};
      if (search) params.search = search;
      if (filterActive !== 'all') params.is_active = filterActive === 'active';

      const response = await api.get('/customers/', { params });
      setCustomers(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load customers');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/customers/stats/');
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const toggleActive = async (customerId) => {
    try {
      await api.post(`/customers/${customerId}/toggle_active/`);
      fetchCustomers();
      fetchStats();
    } catch (err) {
      alert('Failed to update customer status');
    }
  };

  return (
    <div className="customers-page">
      <div className="page-header">
        <div>
          <h2>👥 Customers</h2>
          <p className="page-subtitle">Manage customer information and contacts</p>
        </div>
        <Link to="/customers/new" className="btn-primary">
          + Add Customer
        </Link>
      </div>

      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Customers</div>
        </div>
        <div className="stat-card active">
          <div className="stat-value">{stats.active}</div>
          <div className="stat-label">Active</div>
        </div>
        <div className="stat-card inactive">
          <div className="stat-value">{stats.inactive}</div>
          <div className="stat-label">Inactive</div>
        </div>
      </div>

      <div className="filters-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by name, mobile, or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          {search && (
            <button 
              onClick={() => setSearch('')}
              className="clear-search"
            >
              ✕
            </button>
          )}
        </div>

        <div className="filter-buttons">
          <button
            className={`filter-btn ${filterActive === 'all' ? 'active' : ''}`}
            onClick={() => setFilterActive('all')}
          >
            All
          </button>
          <button
            className={`filter-btn ${filterActive === 'active' ? 'active' : ''}`}
            onClick={() => setFilterActive('active')}
          >
            Active
          </button>
          <button
            className={`filter-btn ${filterActive === 'inactive' ? 'active' : ''}`}
            onClick={() => setFilterActive('inactive')}
          >
            Inactive
          </button>
        </div>
      </div>

      {loading && <div className="loading">Loading customers...</div>}
      {error && <div className="error-message">{error}</div>}

      {!loading && !error && (
        <div className="customers-table-card">
          {customers.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">👥</div>
              <h3>No customers found</h3>
              <p>
                {search 
                  ? 'Try adjusting your search terms' 
                  : 'Get started by adding your first customer'}
              </p>
              {!search && (
                <Link to="/customers/new" className="btn-primary">
                  + Add First Customer
                </Link>
              )}
            </div>
          ) : (
            <table className="customers-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Mobile</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Added</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((customer) => (
                  <tr key={customer.id}>
                    <td>
                      <Link to={`/customers/${customer.id}`} className="customer-name">
                        {customer.name}
                      </Link>
                    </td>
                    <td>{customer.mobile}</td>
                    <td>{customer.email || '-'}</td>
                    <td>
                      <span className={`status-badge ${customer.is_active ? 'active' : 'inactive'}`}>
                        {customer.status}
                      </span>
                    </td>
                    <td>{new Date(customer.created_at).toLocaleDateString()}</td>
                    <td>
                      <div className="action-buttons">
                        <Link 
                          to={`/customers/${customer.id}/edit`}
                          className="btn-icon"
                          title="Edit"
                        >
                          ✏️
                        </Link>
                        <button
                          onClick={() => toggleActive(customer.id)}
                          className="btn-icon"
                          title={customer.is_active ? 'Deactivate' : 'Activate'}
                        >
                          {customer.is_active ? '🔒' : '🔓'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
};

export default Customers;

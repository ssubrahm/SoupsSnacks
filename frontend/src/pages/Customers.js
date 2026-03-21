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
  const [filterApartment, setFilterApartment] = useState('');
  const [filterBlock, setFilterBlock] = useState('');
  const [apartments, setApartments] = useState([]);
  const [blocks, setBlocks] = useState([]);
  const [stats, setStats] = useState({ total: 0, active: 0, inactive: 0 });

  useEffect(() => {
    fetchCustomers();
    fetchStats();
  }, [search, filterActive, filterApartment, filterBlock]);

  useEffect(() => {
    fetchApartments();
  }, []);

  useEffect(() => {
    if (filterApartment) {
      fetchBlocks();
    } else {
      setBlocks([]);
      setFilterBlock('');
    }
  }, [filterApartment]);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const params = {};
      if (search) params.search = search;
      if (filterActive !== 'all') params.is_active = filterActive === 'active';
      if (filterApartment) params.apartment_name = filterApartment;
      if (filterBlock) params.block = filterBlock;

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

  const fetchApartments = async () => {
    try {
      const response = await api.get('/customers/apartments/');
      setApartments(response.data);
    } catch (err) {
      console.error('Failed to load apartments:', err);
    }
  };

  const fetchBlocks = async () => {
    try {
      const params = filterApartment ? { apartment_name: filterApartment } : {};
      const response = await api.get('/customers/blocks/', { params });
      setBlocks(response.data);
    } catch (err) {
      console.error('Failed to load blocks:', err);
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
            placeholder="Search by name, mobile, email, apartment, or block..."
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

        <div className="filter-row">
          <div className="filter-group">
            <label>Status:</label>
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

          <div className="filter-group">
            <label htmlFor="apartment-filter">Apartment:</label>
            <select
              id="apartment-filter"
              value={filterApartment}
              onChange={(e) => setFilterApartment(e.target.value)}
              className="filter-select"
            >
              <option value="">All Apartments</option>
              {apartments.map(apt => (
                <option key={apt} value={apt}>{apt}</option>
              ))}
            </select>
          </div>

          {filterApartment && blocks.length > 0 && (
            <div className="filter-group">
              <label htmlFor="block-filter">Block:</label>
              <select
                id="block-filter"
                value={filterBlock}
                onChange={(e) => setFilterBlock(e.target.value)}
                className="filter-select"
              >
                <option value="">All Blocks</option>
                {blocks.map(blk => (
                  <option key={blk} value={blk}>{blk}</option>
                ))}
              </select>
            </div>
          )}
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
                  <th className="hide-mobile">Email</th>
                  <th>Apartment</th>
                  <th className="hide-mobile">Block</th>
                  <th>Status</th>
                  <th className="hide-mobile">Added</th>
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
                    <td className="hide-mobile">{customer.email || '-'}</td>
                    <td>{customer.apartment_name || '-'}</td>
                    <td className="hide-mobile">{customer.block || '-'}</td>
                    <td>
                      <span className={`status-badge ${customer.is_active ? 'active' : 'inactive'}`}>
                        {customer.status}
                      </span>
                    </td>
                    <td className="hide-mobile">{new Date(customer.created_at).toLocaleDateString()}</td>
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

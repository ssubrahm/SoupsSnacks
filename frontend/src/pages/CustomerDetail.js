import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import './CustomerDetail.css';

const CustomerDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCustomer();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const fetchCustomer = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/customers/customers/${id}/`);
      setCustomer(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load customer');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleActive = async () => {
    try {
      await api.post(`/customers/customers/${id}/toggle_active/`);
      fetchCustomer();
    } catch (err) {
      alert('Failed to update customer status');
    }
  };

  if (loading) {
    return <div className="loading">Loading customer...</div>;
  }

  if (error || !customer) {
    return (
      <div className="error-page">
        <h2>Customer Not Found</h2>
        <p>{error}</p>
        <Link to="/customers" className="btn-primary">← Back to Customers</Link>
      </div>
    );
  }

  return (
    <div className="customer-detail-page">
      <div className="detail-header">
        <div>
          <h2>{customer.name}</h2>
          <span className={`status-badge ${customer.is_active ? 'active' : 'inactive'}`}>
            {customer.status}
          </span>
        </div>
        <div className="header-actions">
          <Link to={`/customers/${id}/edit`} className="btn-primary">
            ✏️ Edit
          </Link>
          <button onClick={toggleActive} className="btn-secondary">
            {customer.is_active ? '🔒 Deactivate' : '🔓 Activate'}
          </button>
          <Link to="/customers" className="btn-secondary">
            ← Back
          </Link>
        </div>
      </div>

      <div className="detail-grid">
        <div className="detail-card">
          <h3>Contact Information</h3>
          
          <div className="detail-item">
            <div className="detail-label">Mobile</div>
            <div className="detail-value">
              <a href={`tel:${customer.mobile}`}>{customer.mobile}</a>
            </div>
          </div>

          {customer.email && (
            <div className="detail-item">
              <div className="detail-label">Email</div>
              <div className="detail-value">
                <a href={`mailto:${customer.email}`}>{customer.email}</a>
              </div>
            </div>
          )}

          {customer.apartment_name && (
            <div className="detail-item">
              <div className="detail-label">Apartment</div>
              <div className="detail-value">{customer.apartment_name}</div>
            </div>
          )}

          {customer.block && (
            <div className="detail-item">
              <div className="detail-label">Block / Tower</div>
              <div className="detail-value">{customer.block}</div>
            </div>
          )}

          {customer.address && (
            <div className="detail-item">
              <div className="detail-label">Full Address</div>
              <div className="detail-value address">{customer.address}</div>
            </div>
          )}
        </div>

        <div className="detail-card">
          <h3>Additional Information</h3>
          
          {customer.notes && (
            <div className="detail-item">
              <div className="detail-label">Notes</div>
              <div className="detail-value notes">{customer.notes}</div>
            </div>
          )}

          <div className="detail-item">
            <div className="detail-label">Customer Since</div>
            <div className="detail-value">
              {new Date(customer.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </div>
          </div>

          <div className="detail-item">
            <div className="detail-label">Last Updated</div>
            <div className="detail-value">
              {new Date(customer.updated_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="detail-card">
        <h3>Order History</h3>
        <div className="empty-state-small">
          <p>No orders yet</p>
          <p className="hint">Order history will appear here in future steps</p>
        </div>
      </div>
    </div>
  );
};

export default CustomerDetail;

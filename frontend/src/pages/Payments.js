import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import './Payments.css';

const Payments = () => {
  const [payments, setPayments] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [filterMethod, setFilterMethod] = useState('');
  const [selectedPayments, setSelectedPayments] = useState([]);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPayments();
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterMethod]);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterMethod) params.method = filterMethod;
      const response = await api.get('/payments/payments/', { params });
      setPayments(response.data);
    } catch (err) {
      console.error('Failed to load payments:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/payments/payments/stats/');
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const formatCurrency = (amount) => `₹${parseFloat(amount || 0).toFixed(2)}`;

  const handleSelectPayment = (id) => {
    setSelectedPayments(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const handleSelectAll = () => {
    setSelectedPayments(selectedPayments.length === payments.length ? [] : payments.map(p => p.id));
  };

  const handleDeleteSelected = async () => {
    if (selectedPayments.length === 0) return;
    const msg = selectedPayments.length === 1 ? 'Delete this payment?' : `Delete ${selectedPayments.length} payments?`;
    if (!window.confirm(msg)) return;
    
    setDeleting(true);
    try {
      await Promise.all(selectedPayments.map(id => api.delete(`/payments/payments/${id}/`)));
      setSelectedPayments([]);
      fetchPayments();
      fetchStats();
    } catch (err) {
      setError('Failed to delete payments');
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteSingle = async (id) => {
    if (!window.confirm('Delete this payment?')) return;
    try {
      await api.delete(`/payments/payments/${id}/`);
      fetchPayments();
      fetchStats();
    } catch (err) {
      setError('Failed to delete payment');
    }
  };

  if (loading) {
    return <div className="loading">Loading payments...</div>;
  }

  return (
    <div className="payments-page">
      <div className="page-header">
        <div>
          <h1>💰 Payments</h1>
          <p className="subtitle">All payment transactions</p>
        </div>
        {selectedPayments.length > 0 && (
          <button onClick={handleDeleteSelected} className="btn-danger" disabled={deleting}>
            🗑️ Delete ({selectedPayments.length})
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-value">{stats.total_payments || 0}</div>
          <div className="stat-label">Total Payments</div>
        </div>
        <div className="stat-card highlight">
          <div className="stat-value">{formatCurrency(stats.total_amount)}</div>
          <div className="stat-label">Total Collected</div>
        </div>
        {stats.by_method && (
          <>
            <div className="stat-card upi">
              <div className="stat-value">{formatCurrency(stats.by_method.upi?.amount)}</div>
              <div className="stat-label">UPI</div>
            </div>
            <div className="stat-card cash">
              <div className="stat-value">{formatCurrency(stats.by_method.cash?.amount)}</div>
              <div className="stat-label">Cash</div>
            </div>
          </>
        )}
      </div>

      <div className="quick-filters">
        <button 
          onClick={() => setFilterMethod('')} 
          className={`filter-chip ${filterMethod === '' ? 'active' : ''}`}
        >
          All Methods
        </button>
        <button 
          onClick={() => setFilterMethod('upi')} 
          className={`filter-chip upi ${filterMethod === 'upi' ? 'active' : ''}`}
        >
          UPI
        </button>
        <button 
          onClick={() => setFilterMethod('cash')} 
          className={`filter-chip cash ${filterMethod === 'cash' ? 'active' : ''}`}
        >
          Cash
        </button>
        <button 
          onClick={() => setFilterMethod('bank_transfer')} 
          className={`filter-chip bank ${filterMethod === 'bank_transfer' ? 'active' : ''}`}
        >
          Bank Transfer
        </button>
        <button 
          onClick={() => setFilterMethod('card')} 
          className={`filter-chip card ${filterMethod === 'card' ? 'active' : ''}`}
        >
          Card
        </button>
      </div>

      {payments.length === 0 ? (
        <div className="empty-state">
          <p>No payments found</p>
          <p className="hint">Payments are added from the Order Detail page</p>
          <Link to="/orders" className="btn-primary">Go to Orders</Link>
        </div>
      ) : (
        <div className="payments-table-container">
          <table className="payments-table">
            <thead>
              <tr>
                <th className="checkbox-col">
                  <input type="checkbox" checked={selectedPayments.length === payments.length && payments.length > 0} onChange={handleSelectAll} />
                </th>
                <th>Date</th>
                <th>Order</th>
                <th>Amount</th>
                <th>Method</th>
                <th>Reference</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((payment) => (
                <tr key={payment.id} className={selectedPayments.includes(payment.id) ? 'selected' : ''}>
                  <td className="checkbox-col">
                    <input type="checkbox" checked={selectedPayments.includes(payment.id)} onChange={() => handleSelectPayment(payment.id)} />
                  </td>
                  <td>{new Date(payment.payment_date).toLocaleDateString()}</td>
                  <td>
                    <Link to={`/orders/${payment.order}`} className="order-link">
                      View Order
                    </Link>
                  </td>
                  <td className="amount">{formatCurrency(payment.amount)}</td>
                  <td>
                    <span className={`method-badge ${payment.method}`}>
                      {payment.method}
                    </span>
                  </td>
                  <td>{payment.reference || '-'}</td>
                  <td>
                    <button onClick={() => handleDeleteSingle(payment.id)} className="btn-icon btn-delete" title="Delete">🗑️</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Payments;

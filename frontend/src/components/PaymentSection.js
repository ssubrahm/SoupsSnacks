import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './PaymentSection.css';

const PaymentSection = ({ orderId, orderTotal, onPaymentAdded }) => {
  const [payments, setPayments] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [paymentData, setPaymentData] = useState({
    payment_date: new Date().toISOString().split('T')[0],
    amount: '',
    method: 'upi',
    reference: '',
    remarks: ''
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPayments();
  }, [orderId]);

  const fetchPayments = async () => {
    try {
      const response = await api.get(`/payments/payments/?order=${orderId}`);
      setPayments(response.data);
    } catch (err) {
      console.error('Failed to load payments:', err);
    }
  };

  const totalPaid = payments.reduce((sum, p) => sum + parseFloat(p.amount), 0);
  const outstanding = orderTotal - totalPaid;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      await api.post('/payments/payments/', {
        ...paymentData,
        order: orderId,
        amount: parseFloat(paymentData.amount)
      });

      // Reset form
      setPaymentData({
        payment_date: new Date().toISOString().split('T')[0],
        amount: '',
        method: 'upi',
        reference: '',
        remarks: ''
      });
      setShowForm(false);
      
      // Refresh payments and notify parent
      await fetchPayments();
      if (onPaymentAdded) onPaymentAdded();
    } catch (err) {
      setError(err.response?.data?.amount?.[0] || 'Failed to add payment');
    } finally {
      setSaving(false);
    }
  };

  const formatCurrency = (amount) => `₹${parseFloat(amount).toFixed(2)}`;

  return (
    <div className="payment-section">
      <div className="payment-header">
        <h3>💳 Payments</h3>
        {outstanding > 0.01 && !showForm && (
          <button onClick={() => setShowForm(true)} className="btn-primary btn-sm">
            + Add Payment
          </button>
        )}
      </div>

      <div className="payment-summary">
        <div className="summary-row">
          <span>Order Total:</span>
          <span className="amount">{formatCurrency(orderTotal)}</span>
        </div>
        <div className="summary-row">
          <span>Total Paid:</span>
          <span className="amount paid">{formatCurrency(totalPaid)}</span>
        </div>
        <div className="summary-row highlight">
          <span>Outstanding:</span>
          <span className={`amount ${outstanding < 0.01 ? 'paid' : 'outstanding'}`}>
            {formatCurrency(outstanding)}
          </span>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="payment-form">
          <h4>Add Payment</h4>
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-row">
            <div className="form-group">
              <label>Payment Date *</label>
              <input
                type="date"
                value={paymentData.payment_date}
                onChange={(e) => setPaymentData({...paymentData, payment_date: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label>Amount (₹) *</label>
              <input
                type="number"
                step="0.01"
                max={outstanding}
                value={paymentData.amount}
                onChange={(e) => setPaymentData({...paymentData, amount: e.target.value})}
                placeholder={`Max: ${outstanding.toFixed(2)}`}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Payment Method *</label>
              <select
                value={paymentData.method}
                onChange={(e) => setPaymentData({...paymentData, method: e.target.value})}
              >
                <option value="upi">UPI</option>
                <option value="cash">Cash</option>
                <option value="bank_transfer">Bank Transfer</option>
                <option value="card">Credit/Debit Card</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label>Reference (UPI ID, etc.)</label>
              <input
                type="text"
                value={paymentData.reference}
                onChange={(e) => setPaymentData({...paymentData, reference: e.target.value})}
                placeholder="Transaction ID"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Remarks</label>
            <textarea
              value={paymentData.remarks}
              onChange={(e) => setPaymentData({...paymentData, remarks: e.target.value})}
              rows="2"
              placeholder="Optional notes"
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? 'Saving...' : 'Add Payment'}
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      )}

      {payments.length > 0 && (
        <div className="payment-history">
          <h4>Payment History</h4>
          <table className="payments-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Amount</th>
                <th>Method</th>
                <th>Reference</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((payment) => (
                <tr key={payment.id}>
                  <td>{new Date(payment.payment_date).toLocaleDateString()}</td>
                  <td className="amount">{formatCurrency(payment.amount)}</td>
                  <td>
                    <span className={`method-badge ${payment.method}`}>
                      {payment.method}
                    </span>
                  </td>
                  <td>{payment.reference || '-'}</td>
                  <td>{payment.remarks || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {payments.length === 0 && (
        <div className="no-payments">
          <p>No payments recorded yet</p>
        </div>
      )}
    </div>
  );
};

export default PaymentSection;

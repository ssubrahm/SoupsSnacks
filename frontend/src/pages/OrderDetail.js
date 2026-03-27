import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import PaymentSection from '../components/PaymentSection';
import './OrderDetail.css';

const OrderDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchOrder();
  }, [id]);

  const fetchOrder = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/orders/orders/${id}/`);
      setOrder(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load order');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const changeStatus = async (newStatus) => {
    try {
      await api.post(`/orders/orders/${id}/change_status/`, { status: newStatus });
      fetchOrder();
    } catch (err) {
      alert('Failed to update status');
    }
  };

  const changePaymentStatus = async (newStatus) => {
    try {
      await api.post(`/orders/orders/${id}/change_payment_status/`, { payment_status: newStatus });
      fetchOrder();
    } catch (err) {
      alert('Failed to update payment status');
    }
  };

  const formatCurrency = (amount) => {
    return `₹${parseFloat(amount).toFixed(2)}`;
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: 'gray',
      confirmed: 'blue',
      preparing: 'orange',
      ready: 'purple',
      delivered: 'green',
      completed: 'teal',
      cancelled: 'red',
    };
    return colors[status] || 'gray';
  };

  if (loading) {
    return <div className="loading">Loading order...</div>;
  }

  if (error || !order) {
    return (
      <div className="error-page">
        <h2>Order Not Found</h2>
        <p>{error}</p>
        <Link to="/orders" className="btn-primary">← Back to Orders</Link>
      </div>
    );
  }

  return (
    <div className="order-detail-page">
      <div className="detail-header">
        <div>
          <h2>{order.order_number}</h2>
          <div className="header-meta">
            <span className={`status-badge ${getStatusColor(order.status)}`}>
              {order.status}
            </span>
            <span className={`payment-badge ${order.payment_status}`}>
              {order.payment_status}
            </span>
            <span className="type-badge">{order.order_type}</span>
          </div>
        </div>
        <div className="header-actions">
          <Link to={`/orders/${id}/edit`} className="btn-primary">
            ✏️ Edit
          </Link>
          <Link to="/orders" className="btn-secondary">
            ← Back
          </Link>
        </div>
      </div>

      <div className="detail-grid">
        {/* Customer Info */}
        <div className="detail-card">
          <h3>👤 Customer</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="label">Name:</span>
              <span className="value">{order.customer_details?.name}</span>
            </div>
            <div className="info-item">
              <span className="label">Mobile:</span>
              <span className="value">{order.customer_details?.mobile}</span>
            </div>
            {order.customer_details?.email && (
              <div className="info-item">
                <span className="label">Email:</span>
                <span className="value">{order.customer_details.email}</span>
              </div>
            )}
            {order.customer_details?.apartment_name && (
              <div className="info-item">
                <span className="label">Apartment:</span>
                <span className="value">
                  {order.customer_details.apartment_name} - {order.customer_details.block}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Order Info */}
        <div className="detail-card">
          <h3>📋 Order Details</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="label">Order Date:</span>
              <span className="value">{new Date(order.order_date).toLocaleDateString()}</span>
            </div>
            <div className="info-item">
              <span className="label">Fulfillment Date:</span>
              <span className="value">
                {order.fulfillment_date 
                  ? new Date(order.fulfillment_date).toLocaleDateString()
                  : 'Not set'
                }
              </span>
            </div>
            <div className="info-item">
              <span className="label">Type:</span>
              <span className="value">{order.order_type}</span>
            </div>
            <div className="info-item">
              <span className="label">Items:</span>
              <span className="value">{order.item_count} items ({order.total_quantity} quantity)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Delivery Info */}
      {order.order_type === 'delivery' && (order.delivery_address || order.delivery_notes) && (
        <div className="detail-card">
          <h3>🚚 Delivery Information</h3>
          {order.delivery_address && (
            <div className="info-item">
              <span className="label">Address:</span>
              <span className="value">{order.delivery_address}</span>
            </div>
          )}
          {order.delivery_notes && (
            <div className="info-item">
              <span className="label">Notes:</span>
              <span className="value">{order.delivery_notes}</span>
            </div>
          )}
        </div>
      )}

      {/* Order Items */}
      <div className="detail-card">
        <h3>🛒 Order Items</h3>
        <div className="items-table-container">
          <table className="items-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Unit</th>
                <th>Qty</th>
                <th>Unit Price</th>
                <th>Unit Cost</th>
                <th>Line Total</th>
                <th>Line Cost</th>
                <th>Line Profit</th>
                <th>Margin</th>
              </tr>
            </thead>
            <tbody>
              {order.items.map((item) => (
                <tr key={item.id}>
                  <td>{item.product_details?.name}</td>
                  <td>{item.product_details?.unit}</td>
                  <td className="qty">{item.quantity}</td>
                  <td className="amount">{formatCurrency(item.unit_price)}</td>
                  <td className="amount cost">{formatCurrency(item.unit_cost_snapshot)}</td>
                  <td className="amount">{formatCurrency(item.line_total)}</td>
                  <td className="amount cost">{formatCurrency(item.line_cost)}</td>
                  <td className="amount profit">{formatCurrency(item.line_profit)}</td>
                  <td className="margin">
                    <span className={`margin-badge ${
                      item.line_margin_percent >= 30 ? 'high' :
                      item.line_margin_percent >= 15 ? 'medium' : 'low'
                    }`}>
                      {parseFloat(item.line_margin_percent).toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="totals-row">
                <td colSpan="5" className="totals-label">Totals:</td>
                <td className="amount total">{formatCurrency(order.total_revenue)}</td>
                <td className="amount cost total">{formatCurrency(order.total_cost)}</td>
                <td className="amount profit total">{formatCurrency(order.total_profit)}</td>
                <td className="margin">
                  <span className={`margin-badge ${
                    order.margin_percent >= 30 ? 'high' :
                    order.margin_percent >= 15 ? 'medium' : 'low'
                  }`}>
                    {parseFloat(order.margin_percent).toFixed(1)}%
                  </span>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* Order Summary */}
      <div className="detail-card summary-card">
        <h3>💰 Order Summary</h3>
        <div className="summary-grid">
          <div className="summary-item">
            <span className="label">Total Revenue:</span>
            <span className="value revenue">{formatCurrency(order.total_revenue)}</span>
          </div>
          <div className="summary-item">
            <span className="label">Total Cost:</span>
            <span className="value cost">{formatCurrency(order.total_cost)}</span>
          </div>
          <div className="summary-item highlight">
            <span className="label">Total Profit:</span>
            <span className="value profit">{formatCurrency(order.total_profit)}</span>
          </div>
          <div className="summary-item">
            <span className="label">Profit Margin:</span>
            <span className={`value margin ${
              order.margin_percent >= 30 ? 'high' :
              order.margin_percent >= 15 ? 'medium' : 'low'
            }`}>
              {parseFloat(order.margin_percent).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Status Management */}
      <div className="detail-grid">
        <div className="detail-card">
          <h3>📊 Change Status</h3>
          <div className="status-buttons">
            {['draft', 'confirmed', 'preparing', 'ready', 'delivered', 'completed', 'cancelled'].map(status => (
              <button
                key={status}
                onClick={() => changeStatus(status)}
                className={`status-btn ${getStatusColor(status)} ${order.status === status ? 'active' : ''}`}
                disabled={order.status === status}
              >
                {status}
              </button>
            ))}
          </div>
        </div>

        <div className="detail-card">
          <h3>💳 Change Payment Status</h3>
          <div className="status-buttons">
            {['pending', 'partial', 'paid', 'refunded'].map(status => (
              <button
                key={status}
                onClick={() => changePaymentStatus(status)}
                className={`payment-btn ${status} ${order.payment_status === status ? 'active' : ''}`}
                disabled={order.payment_status === status}
              >
                {status}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Notes */}
      {order.notes && (
        <div className="detail-card">
          <h3>📝 Internal Notes</h3>
          <p className="notes">{order.notes}</p>
        </div>
      )}

      {/* Payment Section */}
      <PaymentSection 
        orderId={order.id}
        orderTotal={order.total_revenue}
        onPaymentAdded={fetchOrder}
      />

      {/* Metadata */}
      <div className="detail-card metadata">
        <div className="metadata-grid">
          <div className="metadata-item">
            <span className="label">Created:</span>
            <span className="value">{new Date(order.created_at).toLocaleString()}</span>
          </div>
          <div className="metadata-item">
            <span className="label">Last Updated:</span>
            <span className="value">{new Date(order.updated_at).toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderDetail;

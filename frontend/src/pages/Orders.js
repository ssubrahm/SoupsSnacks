import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import './Orders.css';

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterPayment, setFilterPayment] = useState('');
  const [stats, setStats] = useState({ total: 0, by_status: {}, by_payment: {} });

  const statuses = [
    { value: '', label: 'All Statuses' },
    { value: 'draft', label: 'Draft' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'preparing', label: 'Preparing' },
    { value: 'ready', label: 'Ready' },
    { value: 'delivered', label: 'Delivered' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
  ];

  const paymentStatuses = [
    { value: '', label: 'All Payment Status' },
    { value: 'pending', label: 'Pending' },
    { value: 'partial', label: 'Partial' },
    { value: 'paid', label: 'Paid' },
    { value: 'refunded', label: 'Refunded' },
  ];

  useEffect(() => {
    fetchOrders();
    fetchStats();
  }, [search, filterStatus, filterPayment]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const params = {};
      if (search) params.search = search;
      if (filterStatus) params.status = filterStatus;
      if (filterPayment) params.payment_status = filterPayment;

      const response = await api.get('/orders/orders/', { params });
      setOrders(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load orders');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/orders/orders/stats/');
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
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

  const getPaymentColor = (paymentStatus) => {
    const colors = {
      pending: 'orange',
      partial: 'yellow',
      paid: 'green',
      refunded: 'red',
    };
    return colors[paymentStatus] || 'gray';
  };

  return (
    <div className="orders-page">
      <div className="page-header">
        <div>
          <h2>🥘 Orders</h2>
          <p className="page-subtitle">Manage customer orders</p>
        </div>
        <Link to="/orders/new" className="btn-primary">
          + Create Order
        </Link>
      </div>

      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Orders</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{formatCurrency(stats.total_revenue || 0)}</div>
          <div className="stat-label">Total Revenue</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{formatCurrency(stats.total_profit || 0)}</div>
          <div className="stat-label">Total Profit</div>
        </div>
      </div>

      <div className="filters-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by order number, customer name, or mobile..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-row">
          <div className="filter-group">
            <label>Status:</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="filter-select"
            >
              {statuses.map(s => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Payment:</label>
            <select
              value={filterPayment}
              onChange={(e) => setFilterPayment(e.target.value)}
              className="filter-select"
            >
              {paymentStatuses.map(p => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading && <div className="loading">Loading orders...</div>}
      {error && <div className="error-message">{error}</div>}

      {!loading && !error && (
        <div className="orders-table-container">
          {orders.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🥘</div>
              <h3>No orders found</h3>
              <p>Get started by creating your first order</p>
              <Link to="/orders/new" className="btn-primary">+ Create First Order</Link>
            </div>
          ) : (
            <table className="orders-table">
              <thead>
                <tr>
                  <th>Order #</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Fulfillment</th>
                  <th>Items</th>
                  <th>Revenue</th>
                  <th>Profit</th>
                  <th>Status</th>
                  <th>Payment</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id}>
                    <td>
                      <Link to={`/orders/${order.id}`} className="order-link">
                        {order.order_number}
                      </Link>
                    </td>
                    <td>
                      <div className="customer-cell">
                        <div className="customer-name">{order.customer_details?.name}</div>
                        <div className="customer-mobile">{order.customer_details?.mobile}</div>
                      </div>
                    </td>
                    <td>{new Date(order.order_date).toLocaleDateString()}</td>
                    <td>
                      {order.fulfillment_date 
                        ? new Date(order.fulfillment_date).toLocaleDateString()
                        : '-'
                      }
                    </td>
                    <td>
                      <span className="items-badge">{order.item_count} items</span>
                      <span className="qty-badge">({order.total_quantity} qty)</span>
                    </td>
                    <td className="amount">{formatCurrency(order.total_revenue)}</td>
                    <td className="amount profit">{formatCurrency(order.total_profit)}</td>
                    <td>
                      <span className={`status-badge ${getStatusColor(order.status)}`}>
                        {order.status}
                      </span>
                    </td>
                    <td>
                      <span className={`payment-badge ${getPaymentColor(order.payment_status)}`}>
                        {order.payment_status}
                      </span>
                    </td>
                    <td className="actions-cell">
                      <Link to={`/orders/${order.id}`} className="btn-icon" title="View">
                        👁️
                      </Link>
                      <Link to={`/orders/${order.id}/edit`} className="btn-icon" title="Edit">
                        ✏️
                      </Link>
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

export default Orders;

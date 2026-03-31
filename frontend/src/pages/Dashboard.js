import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { formatCurrency } from '../utils/formatters';
import './Dashboard.css';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await api.get('/reports/dashboard/');
      setData(response.data);
      setError(null);
    } catch (err) {
      console.error('Dashboard error:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  // Use compact format for large numbers
  const formatDashboardCurrency = (amount) => formatCurrency(amount, true);

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="error-state">
          <p>{error}</p>
          <button onClick={fetchDashboard} className="btn-primary">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>📊 Dashboard</h1>
        <p className="subtitle">Business overview at a glance</p>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card today">
          <div className="kpi-icon">📦</div>
          <div className="kpi-content">
            <div className="kpi-value">{data?.orders_today || 0}</div>
            <div className="kpi-label">Orders Today</div>
          </div>
        </div>

        <div className="kpi-card pending">
          <div className="kpi-icon">⏳</div>
          <div className="kpi-content">
            <div className="kpi-value">{data?.pending_orders || 0}</div>
            <div className="kpi-label">Pending Orders</div>
          </div>
        </div>

        <div className="kpi-card sales">
          <div className="kpi-icon">💰</div>
          <div className="kpi-content">
            <div className="kpi-value">{formatDashboardCurrency(data?.sales_today)}</div>
            <div className="kpi-label">Sales Today</div>
          </div>
        </div>

        <div className="kpi-card month">
          <div className="kpi-icon">📈</div>
          <div className="kpi-content">
            <div className="kpi-value">{formatDashboardCurrency(data?.sales_month)}</div>
            <div className="kpi-label">Sales This Month</div>
          </div>
        </div>

        <div className="kpi-card profit">
          <div className="kpi-icon">🎯</div>
          <div className="kpi-content">
            <div className="kpi-value">{formatDashboardCurrency(data?.profit_month)}</div>
            <div className="kpi-label">Profit This Month</div>
          </div>
        </div>

        <div className="kpi-card unpaid">
          <div className="kpi-icon">⚠️</div>
          <div className="kpi-content">
            <div className="kpi-value">{formatDashboardCurrency(data?.unpaid_amount)}</div>
            <div className="kpi-label">Unpaid Amount</div>
          </div>
        </div>
      </div>

      {/* Top Lists */}
      <div className="dashboard-grid">
        {/* Top Products */}
        <div className="dashboard-card">
          <div className="card-header">
            <h3>🏆 Top Products (This Month)</h3>
            <Link to="/reports?tab=products" className="view-all">View All →</Link>
          </div>
          <div className="card-content">
            {data?.top_products?.length > 0 ? (
              <table className="mini-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Qty</th>
                    <th>Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {data.top_products.map((product, idx) => (
                    <tr key={idx}>
                      <td>
                        <span className="rank">{idx + 1}</span>
                        {product.product__name}
                      </td>
                      <td>{product.total_qty}</td>
                      <td>{formatCurrency(product.total_revenue)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-message">No sales data yet</p>
            )}
          </div>
        </div>

        {/* Top Customers */}
        <div className="dashboard-card">
          <div className="card-header">
            <h3>⭐ Top Customers (This Month)</h3>
            <Link to="/reports?tab=customers" className="view-all">View All →</Link>
          </div>
          <div className="card-content">
            {data?.top_customers?.length > 0 ? (
              <table className="mini-table">
                <thead>
                  <tr>
                    <th>Customer</th>
                    <th>Orders</th>
                    <th>Spent</th>
                  </tr>
                </thead>
                <tbody>
                  {data.top_customers.map((customer, idx) => (
                    <tr key={idx}>
                      <td>
                        <span className="rank">{idx + 1}</span>
                        {customer.customer__name}
                      </td>
                      <td>{customer.order_count}</td>
                      <td>{formatCurrency(customer.total_spent)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-message">No customer data yet</p>
            )}
          </div>
        </div>

        {/* Order Status */}
        <div className="dashboard-card">
          <div className="card-header">
            <h3>📋 Order Status</h3>
          </div>
          <div className="card-content">
            {data?.status_counts?.length > 0 ? (
              <div className="status-bars">
                {data.status_counts.map((status, idx) => (
                  <div key={idx} className="status-row">
                    <span className={`status-badge ${status.status}`}>
                      {status.status}
                    </span>
                    <div className="status-bar-container">
                      <div 
                        className={`status-bar ${status.status}`}
                        style={{ 
                          width: `${Math.min(100, (status.count / Math.max(...data.status_counts.map(s => s.count))) * 100)}%` 
                        }}
                      ></div>
                    </div>
                    <span className="status-count">{status.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-message">No orders yet</p>
            )}
          </div>
        </div>

        {/* Payment Status */}
        <div className="dashboard-card">
          <div className="card-header">
            <h3>💳 Payment Status</h3>
            <Link to="/reports?tab=unpaid" className="view-all">View Unpaid →</Link>
          </div>
          <div className="card-content">
            {data?.payment_counts?.length > 0 ? (
              <div className="payment-summary">
                {data.payment_counts.map((payment, idx) => (
                  <div key={idx} className={`payment-pill ${payment.payment_status}`}>
                    <span className="payment-label">{payment.payment_status}</span>
                    <span className="payment-count">{payment.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-message">No payment data yet</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <Link to="/orders/new" className="action-btn primary">
            ➕ New Order
          </Link>
          <Link to="/customers/new" className="action-btn secondary">
            👤 Add Customer
          </Link>
          <Link to="/products/new" className="action-btn secondary">
            🍛 Add Product
          </Link>
          <Link to="/reports" className="action-btn secondary">
            📊 View Reports
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

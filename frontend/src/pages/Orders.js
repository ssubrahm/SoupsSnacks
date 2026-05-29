import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import CollapsibleSection from '../components/CollapsibleSection';
import './Orders.css';

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [filterProduct, setFilterProduct] = useState('');
  const [filterStartDate, setFilterStartDate] = useState('');
  const [filterEndDate, setFilterEndDate] = useState('');
  const [filterDateField, setFilterDateField] = useState('order_date');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterPayment, setFilterPayment] = useState('');
  const [stats, setStats] = useState({ total: 0, by_status: {}, by_payment: {} });
  const [showImport, setShowImport] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [selectedOrders, setSelectedOrders] = useState([]);
  const [deleting, setDeleting] = useState(false);

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

  const buildFilterParams = () => {
    const params = {};
    if (search) params.search = search;
    if (filterProduct) params.product_search = filterProduct;
    if (filterStartDate) params.start_date = filterStartDate;
    if (filterEndDate) params.end_date = filterEndDate;
    if (filterStartDate || filterEndDate) params.date_field = filterDateField;
    if (filterStatus) params.status = filterStatus;
    if (filterPayment) params.payment_status = filterPayment;
    return params;
  };

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (search) count += 1;
    if (filterProduct) count += 1;
    if (filterStartDate) count += 1;
    if (filterEndDate) count += 1;
    if (filterStatus) count += 1;
    if (filterPayment) count += 1;
    return count;
  }, [search, filterProduct, filterStartDate, filterEndDate, filterStatus, filterPayment]);

  const filterSummary = useMemo(() => {
    const parts = [];
    if (filterProduct) parts.push(`Product: ${filterProduct}`);
    if (filterStartDate || filterEndDate) {
      const from = filterStartDate || '…';
      const to = filterEndDate || '…';
      const label = filterDateField === 'fulfillment_date' ? 'Fulfillment' : 'Order date';
      parts.push(`${label}: ${from} → ${to}`);
    }
    if (filterStatus) parts.push(`Status: ${filterStatus}`);
    if (filterPayment) parts.push(`Payment: ${filterPayment}`);
    if (search) parts.push(`Search: ${search}`);
    return parts.join(' · ') || 'No filters applied';
  }, [
    search,
    filterProduct,
    filterStartDate,
    filterEndDate,
    filterDateField,
    filterStatus,
    filterPayment,
  ]);

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    fetchOrders();
    fetchStats();
  }, [
    search,
    filterProduct,
    filterStartDate,
    filterEndDate,
    filterDateField,
    filterStatus,
    filterPayment,
  ]);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/catalog/products/', {
        params: { is_active: true },
      });
      setProducts(response.data);
    } catch (err) {
      console.error('Failed to load products:', err);
    }
  };

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await api.get('/orders/orders/', { params: buildFilterParams() });
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
      const response = await api.get('/orders/orders/stats/', { params: buildFilterParams() });
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const clearFilters = () => {
    setSearch('');
    setFilterProduct('');
    setFilterStartDate('');
    setFilterEndDate('');
    setFilterDateField('order_date');
    setFilterStatus('');
    setFilterPayment('');
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

  const handleImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setImporting(true);
    setImportResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/orders/orders/import_csv/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setImportResult(response.data);
      fetchOrders();
      fetchStats();
    } catch (err) {
      setImportResult({
        success: false,
        error: err.response?.data?.error || 'Import failed',
      });
    } finally {
      setImporting(false);
      e.target.value = '';
    }
  };

  const handleSelectOrder = (orderId) => {
    setSelectedOrders((prev) =>
      prev.includes(orderId) ? prev.filter((id) => id !== orderId) : [...prev, orderId]
    );
  };

  const handleSelectAll = () => {
    if (selectedOrders.length === orders.length) {
      setSelectedOrders([]);
    } else {
      setSelectedOrders(orders.map((o) => o.id));
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedOrders.length === 0) return;

    const confirmMsg =
      selectedOrders.length === 1
        ? 'Are you sure you want to delete this order?'
        : `Are you sure you want to delete ${selectedOrders.length} orders?`;

    if (!window.confirm(confirmMsg)) return;

    setDeleting(true);
    try {
      await Promise.all(selectedOrders.map((id) => api.delete(`/orders/orders/${id}/`)));
      setSelectedOrders([]);
      fetchOrders();
      fetchStats();
    } catch (err) {
      setError('Failed to delete orders');
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteSingle = async (orderId, orderNumber) => {
    if (!window.confirm(`Delete order ${orderNumber}?`)) return;

    try {
      await api.delete(`/orders/orders/${orderId}/`);
      fetchOrders();
      fetchStats();
    } catch (err) {
      setError('Failed to delete order');
    }
  };

  const productOptions = products.map((p) => ({
    label: `${p.name} ${p.unit}`.trim(),
    value: p.name,
  }));

  return (
    <div className="orders-page">
      <div className="page-header">
        <div>
          <h2>🥘 Orders</h2>
          <p className="page-subtitle">Manage customer orders</p>
        </div>
        <div className="header-actions">
          {selectedOrders.length > 0 && (
            <button onClick={handleDeleteSelected} className="btn-danger" disabled={deleting}>
              🗑️ Delete ({selectedOrders.length})
            </button>
          )}
          <button onClick={() => setShowImport(!showImport)} className="btn-secondary">
            📥 Import CSV
          </button>
          <Link to="/orders/new" className="btn-primary">
            + Create Order
          </Link>
        </div>
      </div>

      {showImport && (
        <div className="import-section">
          <h3>📊 Import Orders from Google Sheets</h3>
          <p className="hint">
            Export your Google Sheet as CSV and upload it here.
            <a href="/GOOGLE_SHEETS_IMPORT_TEMPLATE.csv" download className="link">
              {' '}
              Download template
            </a>
          </p>

          <div className="file-upload">
            <input
              type="file"
              accept=".csv"
              onChange={handleImport}
              disabled={importing}
              id="csv-upload"
              className="file-input"
            />
            <label htmlFor="csv-upload" className="file-label">
              {importing ? 'Importing...' : 'Choose CSV File'}
            </label>
          </div>

          {importResult && (
            <div className={`import-result ${importResult.success ? 'success' : 'error'}`}>
              {importResult.success ? (
                <>
                  <h4>✅ Import Successful</h4>
                  <p>{importResult.message}</p>
                  <p>
                    <strong>Orders Created:</strong> {importResult.orders_created}
                  </p>
                  {importResult.errors && importResult.errors.length > 0 && (
                    <>
                      <h5>⚠️ Warnings:</h5>
                      <ul>
                        {importResult.errors.map((err, idx) => (
                          <li key={idx}>{err}</li>
                        ))}
                      </ul>
                    </>
                  )}
                </>
              ) : (
                <>
                  <h4>❌ Import Failed</h4>
                  <p>{importResult.error}</p>
                </>
              )}
              <button onClick={() => setImportResult(null)} className="btn-secondary btn-sm">
                Close
              </button>
            </div>
          )}
        </div>
      )}

      <CollapsibleSection
        title="Summary"
        subtitle={`${stats.total} orders · ${formatCurrency(stats.total_revenue || 0)} revenue`}
        badge={stats.total ? String(stats.total) : null}
        storageKey="orders-panel-summary"
        defaultOpen={true}
      >
        <div className="stats-cards orders-stats-cards">
          <div className="stat-card">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Matching Orders</div>
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

        <div className="quick-filters orders-quick-filters">
          <button
            onClick={() => setFilterPayment('')}
            className={`filter-chip ${filterPayment === '' ? 'active' : ''}`}
          >
            All Payments
          </button>
          <button
            onClick={() => setFilterPayment('pending')}
            className={`filter-chip pending ${filterPayment === 'pending' ? 'active' : ''}`}
          >
            💸 Unpaid
          </button>
          <button
            onClick={() => setFilterPayment('partial')}
            className={`filter-chip partial ${filterPayment === 'partial' ? 'active' : ''}`}
          >
            ⏳ Partial
          </button>
          <button
            onClick={() => setFilterPayment('paid')}
            className={`filter-chip paid ${filterPayment === 'paid' ? 'active' : ''}`}
          >
            ✅ Paid
          </button>
        </div>
      </CollapsibleSection>

      <CollapsibleSection
        title="Search & Filters"
        subtitle={filterSummary}
        badge={activeFilterCount > 0 ? `${activeFilterCount} active` : null}
        storageKey="orders-panel-filters"
        defaultOpen={true}
      >
        <div className="orders-filters-inner">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search by order number, customer name, or mobile..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="filter-row orders-filter-row">
            <div className="filter-group filter-group-product">
              <label htmlFor="filter-product">Product:</label>
              <input
                id="filter-product"
                type="text"
                list="order-product-options"
                placeholder="e.g. Tender Mango Pickle 500g"
                value={filterProduct}
                onChange={(e) => setFilterProduct(e.target.value)}
                className="filter-input"
              />
              <datalist id="order-product-options">
                {productOptions.map((opt) => (
                  <option key={opt.label} value={opt.label} />
                ))}
              </datalist>
            </div>

            <div className="filter-group">
              <label htmlFor="filter-date-field">Date type:</label>
              <select
                id="filter-date-field"
                value={filterDateField}
                onChange={(e) => setFilterDateField(e.target.value)}
                className="filter-select"
              >
                <option value="order_date">Order date</option>
                <option value="fulfillment_date">Fulfillment date</option>
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="filter-start-date">From:</label>
              <input
                id="filter-start-date"
                type="date"
                value={filterStartDate}
                onChange={(e) => setFilterStartDate(e.target.value)}
                className="filter-input filter-date"
              />
            </div>

            <div className="filter-group">
              <label htmlFor="filter-end-date">To:</label>
              <input
                id="filter-end-date"
                type="date"
                value={filterEndDate}
                onChange={(e) => setFilterEndDate(e.target.value)}
                className="filter-input filter-date"
              />
            </div>

            <div className="filter-group">
              <label htmlFor="filter-status">Status:</label>
              <select
                id="filter-status"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="filter-select"
              >
                {statuses.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="filter-payment">Payment:</label>
              <select
                id="filter-payment"
                value={filterPayment}
                onChange={(e) => setFilterPayment(e.target.value)}
                className="filter-select"
              >
                {paymentStatuses.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>

            {activeFilterCount > 0 && (
              <button type="button" className="btn-secondary btn-sm clear-filters-btn" onClick={clearFilters}>
                Clear filters
              </button>
            )}
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection
        title="Order list"
        subtitle={loading ? 'Loading…' : `${orders.length} order${orders.length === 1 ? '' : 's'} shown`}
        badge={!loading && orders.length ? String(orders.length) : null}
        storageKey="orders-panel-list"
        defaultOpen={true}
        className="orders-list-panel"
      >
        {loading && <div className="loading">Loading orders...</div>}
        {error && <div className="error-message">{error}</div>}

        {!loading && !error && (
          <div className="orders-table-container">
            {orders.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🥘</div>
                <h3>No orders found</h3>
                <p>Try adjusting your filters or create a new order</p>
                <Link to="/orders/new" className="btn-primary">
                  + Create Order
                </Link>
              </div>
            ) : (
              <table className="orders-table">
                <thead>
                  <tr>
                    <th className="checkbox-col">
                      <input
                        type="checkbox"
                        checked={selectedOrders.length === orders.length && orders.length > 0}
                        onChange={handleSelectAll}
                      />
                    </th>
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
                    <tr key={order.id} className={selectedOrders.includes(order.id) ? 'selected' : ''}>
                      <td className="checkbox-col">
                        <input
                          type="checkbox"
                          checked={selectedOrders.includes(order.id)}
                          onChange={() => handleSelectOrder(order.id)}
                        />
                      </td>
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
                          : '-'}
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
                        <button
                          className="btn-icon btn-delete"
                          title="Delete"
                          onClick={() => handleDeleteSingle(order.id, order.order_number)}
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </CollapsibleSection>
    </div>
  );
};

export default Orders;

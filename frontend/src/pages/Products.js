import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import './Products.css';

const Products = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [filterActive, setFilterActive] = useState('all');
  const [filterCategory, setFilterCategory] = useState('');
  const [stats, setStats] = useState({ total: 0, active: 0, inactive: 0, by_category: {} });

  const categories = [
    { value: '', label: 'All Categories' },
    { value: 'soups', label: 'Soups' },
    { value: 'snacks', label: 'Snacks' },
    { value: 'sweets', label: 'Sweets' },
    { value: 'lunch', label: 'Lunch' },
    { value: 'dinner', label: 'Dinner' },
    { value: 'pickle', label: 'Pickle' },
    { value: 'combos', label: 'Combos' },
    { value: 'other', label: 'Other' },
  ];

  useEffect(() => {
    fetchProducts();
    fetchStats();
  }, [search, filterActive, filterCategory]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = {};
      if (search) params.search = search;
      if (filterActive !== 'all') params.is_active = filterActive === 'active';
      if (filterCategory) params.category = filterCategory;

      const response = await api.get('/catalog/products/', { params });
      setProducts(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load products');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/catalog/products/stats/');
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const toggleActive = async (productId) => {
    try {
      await api.post(`/catalog/products/${productId}/toggle_active/`);
      fetchProducts();
      fetchStats();
    } catch (err) {
      alert('Failed to update product status');
    }
  };

  const formatCurrency = (amount) => {
    return `₹${parseFloat(amount).toFixed(2)}`;
  };

  const getMarginColor = (margin) => {
    const marginNum = parseFloat(margin);
    if (marginNum >= 30) return 'high';
    if (marginNum >= 15) return 'medium';
    return 'low';
  };

  return (
    <div className="products-page">
      <div className="page-header">
        <div>
          <h2>🍛 Product Catalog</h2>
          <p className="page-subtitle">Manage menu items with cost tracking</p>
        </div>
        <Link to="/catalog/new" className="btn-primary">
          + Add Product
        </Link>
      </div>

      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Products</div>
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
            placeholder="Search products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          {search && (
            <button onClick={() => setSearch('')} className="clear-search">✕</button>
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
            <label htmlFor="category-filter">Category:</label>
            <select
              id="category-filter"
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="filter-select"
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>{cat.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading && <div className="loading">Loading products...</div>}
      {error && <div className="error-message">{error}</div>}

      {!loading && !error && (
        <div className="products-grid">
          {products.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🍛</div>
              <h3>No products found</h3>
              <p>{search ? 'Try adjusting your search' : 'Get started by adding your first product'}</p>
              {!search && (
                <Link to="/catalog/new" className="btn-primary">+ Add First Product</Link>
              )}
            </div>
          ) : (
            products.map((product) => (
              <div key={product.id} className="product-card">
                {product.display_image_url && (
                  <div className="product-image">
                    <img src={product.display_image_url} alt={product.name} />
                  </div>
                )}
                <div className="product-header">
                  <Link to={`/catalog/${product.id}`} className="product-title">
                    {product.name}
                  </Link>
                  <span className={`category-badge ${product.category}`}>
                    {product.category}
                  </span>
                </div>

                <div className="product-unit">{product.unit}</div>

                <div className="product-pricing">
                  <div className="pricing-row">
                    <span className="label">Selling Price:</span>
                    <span className="value price">{formatCurrency(product.selling_price)}</span>
                  </div>
                  <div className="pricing-row">
                    <span className="label">Cost:</span>
                    <span className="value cost">{formatCurrency(product.unit_cost)}</span>
                  </div>
                  <div className="pricing-row highlight">
                    <span className="label">Profit:</span>
                    <span className="value profit">{formatCurrency(product.unit_profit)}</span>
                  </div>
                  <div className="pricing-row">
                    <span className="label">Margin:</span>
                    <span className={`value margin ${getMarginColor(product.margin_percent)}`}>
                      {parseFloat(product.margin_percent).toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="product-meta">
                  <span className="component-count">
                    📊 {product.component_count} cost items
                  </span>
                  <span className={`status-badge ${product.is_active ? 'active' : 'inactive'}`}>
                    {product.status}
                  </span>
                </div>

                <div className="product-actions">
                  <Link to={`/catalog/${product.id}/edit`} className="btn-icon" title="Edit">
                    ✏️
                  </Link>
                  <button
                    onClick={() => toggleActive(product.id)}
                    className="btn-icon"
                    title={product.is_active ? 'Deactivate' : 'Activate'}
                  >
                    {product.is_active ? '🔒' : '🔓'}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default Products;

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import './DailyOfferings.css';

const DailyOfferings = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [currentOffering, setCurrentOffering] = useState(null);
  const [products, setProducts] = useState([]);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [notes, setNotes] = useState('');
  const [stats, setStats] = useState({ total: 0, active: 0, inactive: 0 });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchProducts();
    fetchStats();
  }, []);

  useEffect(() => {
    if (selectedDate) {
      fetchOfferingForDate(selectedDate);
    }
  }, [selectedDate]);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/catalog/products/', { params: { is_active: true } });
      console.log('Loaded products:', response.data.length, 'products');
      setProducts(response.data);
    } catch (err) {
      console.error('Failed to load products:', err.response || err);
      setError('Failed to load products: ' + (err.response?.data?.detail || err.message));
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/offerings/daily-offerings/stats/');
      setStats(response.data);
    } catch (err) {
      console.error('Failed to load stats:', err.response || err);
      // Don't show error to user for stats, just use defaults
      setStats({ total: 0, active: 0, inactive: 0 });
    }
  };

  const fetchOfferingForDate = async (date) => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/offerings/daily-offerings/', { params: { date } });
      
      if (response.data.length > 0) {
        const offering = response.data[0];
        console.log('Loaded offering:', offering);
        setCurrentOffering(offering);
        setNotes(offering.notes || '');
        
        // Safely map items with fallback
        if (offering.items && Array.isArray(offering.items)) {
          setSelectedProducts(offering.items.map(item => ({
            product: item.product,
            available_quantity: item.available_quantity || '',
            display_order: item.display_order || 0,
            product_details: item.product_details // Keep full product info
          })));
        } else {
          console.warn('Offering items is not an array:', offering.items);
          setSelectedProducts([]);
        }
      } else {
        setCurrentOffering(null);
        setNotes('');
        setSelectedProducts([]);
      }
    } catch (err) {
      console.error('Error fetching offering:', err.response || err);
      if (err.response?.status === 404) {
        // No offering for this date, which is fine
        setCurrentOffering(null);
        setNotes('');
        setSelectedProducts([]);
        setError('');
      } else {
        setError('Failed to load offering: ' + (err.response?.data?.detail || err.message));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleProductToggle = (productId) => {
    setSelectedProducts(prev => {
      const exists = prev.find(p => p.product === productId);
      if (exists) {
        return prev.filter(p => p.product !== productId);
      } else {
        return [...prev, { product: productId, available_quantity: '', display_order: prev.length }];
      }
    });
  };

  const handleQuantityChange = (productId, quantity) => {
    setSelectedProducts(prev =>
      prev.map(p =>
        p.product === productId
          ? { ...p, available_quantity: quantity === '' ? null : parseInt(quantity) }
          : p
      )
    );
  };

  const handleSave = async () => {
    if (!selectedProducts || selectedProducts.length === 0) {
      alert('Please select at least one product');
      return;
    }

    try {
      setSaving(true);
      const payload = {
        offering_date: selectedDate,
        notes: notes || '',
        is_active: true,
        items: selectedProducts.map((p, idx) => ({
          product: p.product,
          available_quantity: p.available_quantity || null,
          display_order: idx
        }))
      };

      if (currentOffering) {
        await api.put(`/offerings/daily-offerings/${currentOffering.id}/`, payload);
      } else {
        await api.post('/offerings/daily-offerings/', payload);
      }

      await fetchOfferingForDate(selectedDate);
      await fetchStats();
      alert('Offering saved successfully!');
    } catch (err) {
      console.error('Error saving offering:', err);
      alert('Failed to save offering: ' + (err.response?.data?.detail || err.message || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handleExportText = async () => {
    if (!currentOffering) {
      alert('Please save the offering first');
      return;
    }

    try {
      const response = await api.get(`/offerings/daily-offerings/${currentOffering.id}/export_text/`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `menu_${selectedDate.replace(/-/g, '')}.txt`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error(err);
      alert('Failed to export text');
    }
  };

  const formatCurrency = (amount) => {
    return `₹${parseFloat(amount).toFixed(2)}`;
  };

  const getProductById = (id) => {
    return products.find(p => p.id === id);
  };

  return (
    <div className="daily-offerings-page">
      <div className="page-header">
        <div>
          <h2>📅 Daily Offerings</h2>
          <p className="page-subtitle">Manage daily menu for customers</p>
        </div>
        {currentOffering && (
          <button onClick={handleExportText} className="btn-primary">
            📥 Export for WhatsApp/Email
          </button>
        )}
      </div>

      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Offerings</div>
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

      <div className="date-selector">
        <label htmlFor="offering-date">Select Date:</label>
        <input
          type="date"
          id="offering-date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="date-input"
        />
        <span className="date-status">
          {loading ? 'Loading...' : currentOffering ? '✓ Offering exists' : '+ New offering'}
        </span>
      </div>

      {loading && <div className="loading">Loading offering...</div>}
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
          <br />
          <small>Check browser console for details</small>
        </div>
      )}

      {!loading && (
        <div className="offering-form">
          <div className="form-card">
            <h3>📝 Notes for this day</h3>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g., Special festival menu, limited items today..."
              rows="3"
              className="notes-textarea"
            />
          </div>

          <div className="form-card">
            <h3>🍽️ Select Products from Catalog</h3>
            <p className="hint">Choose items to offer on {new Date(selectedDate).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
            
            {products.length === 0 ? (
              <div className="empty-state">
                <p>No active products in catalog. Add products first.</p>
                <Link to="/catalog/new" className="btn-primary">+ Add Product</Link>
              </div>
            ) : (
              <div className="products-selection">
                {products.map(product => {
                  const isSelected = selectedProducts && selectedProducts.some(p => p.product === product.id);
                  const selectedProduct = selectedProducts && selectedProducts.find(p => p.product === product.id);
                  
                  return (
                    <div key={product.id} className={`product-selector ${isSelected ? 'selected' : ''}`}>
                      <div className="product-info">
                        <label className="checkbox-label">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => handleProductToggle(product.id)}
                          />
                          <div className="product-details">
                            <div className="product-name">{product.name}</div>
                            <div className="product-meta">
                              <span className={`category-badge ${product.category}`}>
                                {product.category}
                              </span>
                              <span className="product-unit">{product.unit}</span>
                              <span className="product-price">{formatCurrency(product.selling_price)}</span>
                            </div>
                          </div>
                        </label>
                      </div>
                      
                      {isSelected && (
                        <div className="quantity-input">
                          <label>Max Qty (optional):</label>
                          <input
                            type="number"
                            min="0"
                            value={selectedProduct?.available_quantity || ''}
                            onChange={(e) => handleQuantityChange(product.id, e.target.value)}
                            placeholder="Unlimited"
                            className="qty-field"
                          />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {selectedProducts && selectedProducts.length > 0 && (
            <div className="form-card summary-card">
              <h3>📋 Selected Items ({selectedProducts.length})</h3>
              <div className="selected-list">
                {selectedProducts.map(sp => {
                  // Use product from catalog if available, otherwise use product_details from API
                  const product = getProductById(sp.product) || sp.product_details;
                  return product ? (
                    <div key={sp.product} className="selected-item">
                      <span className="item-name">{product.name} ({product.unit})</span>
                      <span className="item-price">{formatCurrency(product.selling_price)}</span>
                      {sp.available_quantity && (
                        <span className="item-qty">Max: {sp.available_quantity}</span>
                      )}
                    </div>
                  ) : (
                    <div key={sp.product} className="selected-item">
                      <span className="item-name">Product ID: {sp.product}</span>
                      <span className="item-price">Loading...</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div className="form-actions">
            <button 
              onClick={handleSave} 
              className="btn-primary" 
              disabled={!selectedProducts || selectedProducts.length === 0 || saving}
            >
              {saving ? 'Saving...' : currentOffering ? '💾 Update Offering' : '➕ Create Offering'}
            </button>
            {currentOffering && (
              <button onClick={handleExportText} className="btn-secondary">
                📥 Export Text
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DailyOfferings;

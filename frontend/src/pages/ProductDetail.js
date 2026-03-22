import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import './ProductDetail.css';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/catalog/products/${id}/`);
      setProduct(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load product');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleActive = async () => {
    try {
      await api.post(`/catalog/products/${id}/toggle_active/`);
      fetchProduct();
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

  const groupComponentsByType = (components) => {
    const grouped = {};
    components.forEach(comp => {
      if (!grouped[comp.item_type]) {
        grouped[comp.item_type] = [];
      }
      grouped[comp.item_type].push(comp);
    });
    return grouped;
  };

  if (loading) {
    return <div className="loading">Loading product...</div>;
  }

  if (error || !product) {
    return (
      <div className="error-page">
        <h2>Product Not Found</h2>
        <p>{error}</p>
        <Link to="/catalog" className="btn-primary">← Back to Catalog</Link>
      </div>
    );
  }

  const groupedComponents = groupComponentsByType(product.cost_components);

  return (
    <div className="product-detail-page">
      <div className="detail-header">
        <div>
          <h2>{product.name}</h2>
          <div className="header-meta">
            <span className={`category-badge ${product.category}`}>
              {product.category}
            </span>
            <span className="unit-badge">{product.unit}</span>
            <span className={`status-badge ${product.is_active ? 'active' : 'inactive'}`}>
              {product.status}
            </span>
          </div>
        </div>
        <div className="header-actions">
          <Link to={`/catalog/${id}/edit`} className="btn-primary">
            ✏️ Edit
          </Link>
          <button onClick={toggleActive} className="btn-secondary">
            {product.is_active ? '🔒 Deactivate' : '🔓 Activate'}
          </button>
          <Link to="/catalog" className="btn-secondary">
            ← Back
          </Link>
        </div>
      </div>

      {product.display_image_url && (
        <div className="detail-card detail-image-card">
          <img src={product.display_image_url} alt={product.name} className="detail-product-image" />
        </div>
      )}

      {product.description && (
        <div className="detail-card">
          <p className="product-description">{product.description}</p>
        </div>
      )}

      <div className="detail-grid">
        {/* Pricing Summary */}
        <div className="detail-card pricing-summary">
          <h3>💰 Pricing Summary</h3>
          
          <div className="pricing-breakdown">
            <div className="pricing-item">
              <span className="label">Selling Price</span>
              <span className="value selling-price">{formatCurrency(product.selling_price)}</span>
            </div>
            
            <div className="pricing-item">
              <span className="label">Total Cost</span>
              <span className="value cost">{formatCurrency(product.unit_cost)}</span>
            </div>
            
            <div className="pricing-divider"></div>
            
            <div className="pricing-item highlight">
              <span className="label">Unit Profit</span>
              <span className={`value profit ${parseFloat(product.unit_profit) < 0 ? 'negative' : ''}`}>
                {formatCurrency(product.unit_profit)}
              </span>
            </div>
            
            <div className="pricing-item">
              <span className="label">Profit Margin</span>
              <span className={`value margin ${getMarginColor(product.margin_percent)}`}>
                {parseFloat(product.margin_percent).toFixed(1)}%
              </span>
            </div>
          </div>

          {parseFloat(product.unit_profit) < 0 && (
            <div className="alert alert-warning">
              ⚠️ Warning: This product has negative profit!
            </div>
          )}

          {parseFloat(product.margin_percent) < 15 && parseFloat(product.unit_profit) >= 0 && (
            <div className="alert alert-info">
              💡 Low margin: Consider reviewing costs or adjusting price.
            </div>
          )}
        </div>

        {/* Cost Breakdown */}
        <div className="detail-card">
          <h3>📊 Cost Breakdown</h3>
          
          {product.cost_components.length === 0 ? (
            <div className="empty-state-small">
              <p>No cost components defined yet</p>
              <Link to={`/catalog/${id}/edit`} className="btn-primary btn-sm">
                Add Cost Components
              </Link>
            </div>
          ) : (
            <div className="cost-breakdown">
              {Object.keys(groupedComponents).map(type => (
                <div key={type} className="cost-type-section">
                  <h4 className="cost-type-header">{type}</h4>
                  <table className="cost-table">
                    <thead>
                      <tr>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Unit</th>
                        <th>Cost/Unit</th>
                        <th>Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {groupedComponents[type].map((comp, idx) => (
                        <tr key={idx}>
                          <td>{comp.item_name}</td>
                          <td>{parseFloat(comp.quantity).toFixed(3)}</td>
                          <td>{comp.unit_of_measure}</td>
                          <td>{formatCurrency(comp.cost_per_unit)}</td>
                          <td className="total-col">{formatCurrency(comp.total_cost)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <div className="type-subtotal">
                    Subtotal: {formatCurrency(
                      groupedComponents[type].reduce((sum, c) => sum + parseFloat(c.total_cost), 0)
                    )}
                  </div>
                </div>
              ))}
              
              <div className="cost-total">
                <span>Total Cost:</span>
                <span>{formatCurrency(product.unit_cost)}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Additional Info */}
      {product.notes && (
        <div className="detail-card">
          <h3>📝 Internal Notes</h3>
          <p className="notes">{product.notes}</p>
        </div>
      )}

      <div className="detail-card metadata">
        <div className="metadata-grid">
          <div className="metadata-item">
            <span className="label">Created:</span>
            <span className="value">
              {new Date(product.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </span>
          </div>
          <div className="metadata-item">
            <span className="label">Last Updated:</span>
            <span className="value">
              {new Date(product.updated_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;

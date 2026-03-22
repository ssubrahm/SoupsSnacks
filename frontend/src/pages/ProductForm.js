import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import api from '../services/api';
import './ProductForm.css';

const ProductForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    name: '',
    category: 'soups',
    unit: '',
    description: '',
    selling_price: '',
    is_active: true,
    notes: '',
    image_url: '',
  });

  const [costComponents, setCostComponents] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const categories = [
    { value: 'soups', label: 'Soups' },
    { value: 'snacks', label: 'Snacks' },
    { value: 'sweets', label: 'Sweets' },
    { value: 'lunch', label: 'Lunch' },
    { value: 'dinner', label: 'Dinner' },
    { value: 'pickle', label: 'Pickle' },
    { value: 'combos', label: 'Combos' },
    { value: 'other', label: 'Other' },
  ];

  const itemTypes = [
    { value: 'ingredient', label: 'Ingredient' },
    { value: 'labor', label: 'Labor' },
    { value: 'fuel', label: 'Fuel' },
    { value: 'packaging', label: 'Packaging' },
    { value: 'transport', label: 'Transport' },
    { value: 'miscellaneous', label: 'Miscellaneous' },
  ];

  useEffect(() => {
    if (isEdit) {
      fetchProduct();
    }
  }, [id]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/catalog/products/${id}/`);
      const product = response.data;
      setFormData({
        name: product.name,
        category: product.category,
        unit: product.unit,
        description: product.description || '',
        selling_price: product.selling_price,
        is_active: product.is_active,
        notes: product.notes || '',
        image_url: product.image_url || '',
      });
      setCostComponents(product.cost_components || []);
    } catch (err) {
      alert('Failed to load product');
      navigate('/catalog');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const addCostComponent = () => {
    setCostComponents([...costComponents, {
      item_name: '',
      item_type: 'ingredient',
      quantity: '',
      unit_of_measure: '',
      cost_per_unit: '',
    }]);
  };

  const updateCostComponent = (index, field, value) => {
    const updated = [...costComponents];
    updated[index][field] = value;
    setCostComponents(updated);
  };

  const removeCostComponent = (index) => {
    setCostComponents(costComponents.filter((_, i) => i !== index));
  };

  const calculateTotalCost = () => {
    return costComponents.reduce((sum, comp) => {
      const qty = parseFloat(comp.quantity) || 0;
      const cost = parseFloat(comp.cost_per_unit) || 0;
      return sum + (qty * cost);
    }, 0);
  };

  const calculateProfit = () => {
    const sellingPrice = parseFloat(formData.selling_price) || 0;
    return sellingPrice - calculateTotalCost();
  };

  const calculateMargin = () => {
    const sellingPrice = parseFloat(formData.selling_price) || 0;
    if (sellingPrice === 0) return 0;
    return (calculateProfit() / sellingPrice) * 100;
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.unit.trim()) newErrors.unit = 'Unit is required';
    if (!formData.selling_price || parseFloat(formData.selling_price) <= 0) {
      newErrors.selling_price = 'Selling price must be greater than 0';
    }

    costComponents.forEach((comp, index) => {
      if (!comp.item_name.trim()) {
        newErrors[`component_${index}_name`] = 'Item name required';
      }
      if (!comp.quantity || parseFloat(comp.quantity) <= 0) {
        newErrors[`component_${index}_quantity`] = 'Valid quantity required';
      }
      if (!comp.unit_of_measure.trim()) {
        newErrors[`component_${index}_uom`] = 'Unit required';
      }
      if (!comp.cost_per_unit || parseFloat(comp.cost_per_unit) <= 0) {
        newErrors[`component_${index}_cost`] = 'Valid cost required';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) return;

    setSubmitting(true);

    const payload = {
      ...formData,
      cost_components: costComponents.map(comp => ({
        item_name: comp.item_name,
        item_type: comp.item_type,
        quantity: parseFloat(comp.quantity),
        unit_of_measure: comp.unit_of_measure,
        cost_per_unit: parseFloat(comp.cost_per_unit),
      }))
    };

    try {
      if (isEdit) {
        await api.put(`/catalog/products/${id}/`, payload);
      } else {
        await api.post('/catalog/products/', payload);
      }
      navigate('/catalog');
    } catch (err) {
      if (err.response?.data) {
        setErrors(err.response.data);
      } else {
        alert('Failed to save product');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading product...</div>;
  }

  const totalCost = calculateTotalCost();
  const profit = calculateProfit();
  const margin = calculateMargin();

  return (
    <div className="product-form-page">
      <div className="form-header">
        <div>
          <h2>{isEdit ? '✏️ Edit Product' : '➕ Add New Product'}</h2>
          <p className="form-subtitle">
            {isEdit ? 'Update product details and costing' : 'Create product with cost breakdown'}
          </p>
        </div>
        <Link to="/catalog" className="btn-secondary">← Back to Catalog</Link>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-layout">
          <div className="form-main">
            <div className="form-card">
              <h3>Basic Information</h3>
              
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="name">Product Name <span className="required">*</span></label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={errors.name ? 'error' : ''}
                    placeholder="e.g., Cream of Tomato Soup"
                  />
                  {errors.name && <span className="error-text">{errors.name}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="unit">Unit/Size <span className="required">*</span></label>
                  <input
                    type="text"
                    id="unit"
                    name="unit"
                    value={formData.unit}
                    onChange={handleChange}
                    className={errors.unit ? 'error' : ''}
                    placeholder="e.g., 250ml, 1 plate"
                  />
                  {errors.unit && <span className="error-text">{errors.unit}</span>}
                  <small className="hint">For different sizes, create separate products</small>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="category">Category <span className="required">*</span></label>
                  <select
                    id="category"
                    name="category"
                    value={formData.category}
                    onChange={handleChange}
                  >
                    {categories.map(cat => (
                      <option key={cat.value} value={cat.value}>{cat.label}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="selling_price">Selling Price (₹) <span className="required">*</span></label>
                  <input
                    type="number"
                    id="selling_price"
                    name="selling_price"
                    value={formData.selling_price}
                    onChange={handleChange}
                    className={errors.selling_price ? 'error' : ''}
                    placeholder="0.00"
                    step="0.01"
                    min="0.01"
                  />
                  {errors.selling_price && <span className="error-text">{errors.selling_price}</span>}
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows="2"
                  placeholder="Product description (optional)"
                />
              </div>

              <div className="form-group">
                <label htmlFor="image_url">Image URL (optional)</label>
                <input
                  type="url"
                  id="image_url"
                  name="image_url"
                  value={formData.image_url}
                  onChange={handleChange}
                  placeholder="https://example.com/image.jpg"
                />
                <small className="hint">Leave empty to use default category image</small>
              </div>

              <div className="form-group">
                <label htmlFor="notes">Internal Notes</label>
                <textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows="2"
                  placeholder="Internal notes (optional)"
                />
              </div>

              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleChange}
                  />
                  <span>Active product (can be offered to customers)</span>
                </label>
              </div>
            </div>

            {/* Cost Components Section */}
            <div className="form-card">
              <div className="section-header">
                <h3>Cost Components</h3>
                <button type="button" onClick={addCostComponent} className="btn-secondary btn-sm">
                  + Add Cost Item
                </button>
              </div>

              {costComponents.length === 0 ? (
                <div className="empty-components">
                  <p>No cost components yet. Add ingredients, labor, fuel, packaging, etc.</p>
                  <button type="button" onClick={addCostComponent} className="btn-primary">
                    + Add First Cost Item
                  </button>
                </div>
              ) : (
                <div className="cost-components-list">
                  {costComponents.map((comp, index) => (
                    <div key={index} className="cost-component-item">
                      <div className="component-header">
                        <span className="component-number">#{index + 1}</span>
                        <button
                          type="button"
                          onClick={() => removeCostComponent(index)}
                          className="btn-remove"
                        >
                          🗑️ Remove
                        </button>
                      </div>

                      <div className="component-fields">
                        <div className="form-row">
                          <div className="form-group">
                            <label>Item Name *</label>
                            <input
                              type="text"
                              value={comp.item_name}
                              onChange={(e) => updateCostComponent(index, 'item_name', e.target.value)}
                              className={errors[`component_${index}_name`] ? 'error' : ''}
                              placeholder="e.g., Tomatoes, Chef time"
                            />
                            {errors[`component_${index}_name`] && (
                              <span className="error-text">{errors[`component_${index}_name`]}</span>
                            )}
                          </div>

                          <div className="form-group">
                            <label>Type *</label>
                            <select
                              value={comp.item_type}
                              onChange={(e) => updateCostComponent(index, 'item_type', e.target.value)}
                            >
                              {itemTypes.map(type => (
                                <option key={type.value} value={type.value}>{type.label}</option>
                              ))}
                            </select>
                          </div>
                        </div>

                        <div className="form-row">
                          <div className="form-group">
                            <label>Quantity *</label>
                            <input
                              type="number"
                              value={comp.quantity}
                              onChange={(e) => updateCostComponent(index, 'quantity', e.target.value)}
                              className={errors[`component_${index}_quantity`] ? 'error' : ''}
                              placeholder="0.000"
                              step="0.001"
                              min="0.001"
                            />
                            {errors[`component_${index}_quantity`] && (
                              <span className="error-text">{errors[`component_${index}_quantity`]}</span>
                            )}
                          </div>

                          <div className="form-group">
                            <label>Unit *</label>
                            <input
                              type="text"
                              value={comp.unit_of_measure}
                              onChange={(e) => updateCostComponent(index, 'unit_of_measure', e.target.value)}
                              className={errors[`component_${index}_uom`] ? 'error' : ''}
                              placeholder="kg, liters, hours"
                            />
                            {errors[`component_${index}_uom`] && (
                              <span className="error-text">{errors[`component_${index}_uom`]}</span>
                            )}
                          </div>

                          <div className="form-group">
                            <label>Cost/Unit (₹) *</label>
                            <input
                              type="number"
                              value={comp.cost_per_unit}
                              onChange={(e) => updateCostComponent(index, 'cost_per_unit', e.target.value)}
                              className={errors[`component_${index}_cost`] ? 'error' : ''}
                              placeholder="0.00"
                              step="0.01"
                              min="0.01"
                            />
                            {errors[`component_${index}_cost`] && (
                              <span className="error-text">{errors[`component_${index}_cost`]}</span>
                            )}
                          </div>

                          <div className="form-group">
                            <label>Total</label>
                            <div className="calculated-value">
                              ₹{((parseFloat(comp.quantity) || 0) * (parseFloat(comp.cost_per_unit) || 0)).toFixed(2)}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Cost Summary Sidebar */}
          <div className="form-sidebar">
            <div className="summary-card sticky">
              <h3>Cost Summary</h3>
              
              <div className="summary-item">
                <span className="label">Selling Price:</span>
                <span className="value price">₹{parseFloat(formData.selling_price || 0).toFixed(2)}</span>
              </div>

              <div className="summary-item">
                <span className="label">Total Cost:</span>
                <span className="value cost">₹{totalCost.toFixed(2)}</span>
              </div>

              <div className="summary-item divider">
                <span className="label">Unit Profit:</span>
                <span className={`value profit ${profit < 0 ? 'negative' : ''}`}>
                  ₹{profit.toFixed(2)}
                </span>
              </div>

              <div className="summary-item">
                <span className="label">Margin:</span>
                <span className={`value margin ${margin < 15 ? 'low' : margin < 30 ? 'medium' : 'high'}`}>
                  {margin.toFixed(1)}%
                </span>
              </div>

              {profit < 0 && (
                <div className="warning-box">
                  ⚠️ Warning: Negative profit! Cost exceeds selling price.
                </div>
              )}

              {margin < 15 && margin >= 0 && (
                <div className="info-box">
                  💡 Tip: Margin is below 15%. Consider adjusting costs or price.
                </div>
              )}

              <div className="summary-actions">
                <button type="submit" className="btn-primary" disabled={submitting}>
                  {submitting ? 'Saving...' : isEdit ? 'Update Product' : 'Create Product'}
                </button>
                <button
                  type="button"
                  onClick={() => navigate('/catalog')}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ProductForm;

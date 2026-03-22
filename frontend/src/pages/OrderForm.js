import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import api from '../services/api';
import './OrderForm.css';

const OrderForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    customer: '',
    order_date: new Date().toISOString().split('T')[0],
    fulfillment_date: '',
    status: 'draft',
    order_type: 'delivery',
    payment_status: 'pending',
    delivery_address: '',
    delivery_notes: '',
    notes: '',
  });

  const [lineItems, setLineItems] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchCustomers();
    fetchProducts();
    if (isEdit) {
      fetchOrder();
    }
  }, [id]);

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/customers/customers/', { params: { is_active: true } });
      setCustomers(response.data);
    } catch (err) {
      console.error('Failed to load customers:', err);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await api.get('/catalog/products/', { params: { is_active: true } });
      setProducts(response.data);
    } catch (err) {
      console.error('Failed to load products:', err);
    }
  };

  const fetchOrder = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/orders/orders/${id}/`);
      const order = response.data;
      
      setFormData({
        customer: order.customer,
        order_date: order.order_date,
        fulfillment_date: order.fulfillment_date || '',
        status: order.status,
        order_type: order.order_type,
        payment_status: order.payment_status,
        delivery_address: order.delivery_address || '',
        delivery_notes: order.delivery_notes || '',
        notes: order.notes || '',
      });

      setLineItems(order.items.map(item => ({
        product: item.product,
        quantity: item.quantity,
        unit_price: item.unit_price,
        unit_cost_snapshot: item.unit_cost_snapshot,
        display_order: item.display_order,
      })));
    } catch (err) {
      alert('Failed to load order');
      navigate('/orders');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const addLineItem = () => {
    setLineItems([...lineItems, {
      product: '',
      quantity: 1,
      unit_price: '',
      unit_cost_snapshot: '',
    }]);
  };

  const updateLineItem = (index, field, value) => {
    const updated = [...lineItems];
    updated[index][field] = value;

    // Auto-fill prices when product is selected
    if (field === 'product' && value) {
      const product = products.find(p => p.id === parseInt(value));
      if (product) {
        updated[index].unit_price = product.selling_price;
        updated[index].unit_cost_snapshot = product.unit_cost;
      }
    }

    setLineItems(updated);
  };

  const removeLineItem = (index) => {
    setLineItems(lineItems.filter((_, i) => i !== index));
  };

  const calculateLineTotal = (item) => {
    const qty = parseFloat(item.quantity) || 0;
    const price = parseFloat(item.unit_price) || 0;
    return qty * price;
  };

  const calculateLineCost = (item) => {
    const qty = parseFloat(item.quantity) || 0;
    const cost = parseFloat(item.unit_cost_snapshot) || 0;
    return qty * cost;
  };

  const calculateTotalRevenue = () => {
    return lineItems.reduce((sum, item) => sum + calculateLineTotal(item), 0);
  };

  const calculateTotalCost = () => {
    return lineItems.reduce((sum, item) => sum + calculateLineCost(item), 0);
  };

  const calculateTotalProfit = () => {
    return calculateTotalRevenue() - calculateTotalCost();
  };

  const calculateMargin = () => {
    const revenue = calculateTotalRevenue();
    if (revenue === 0) return 0;
    return (calculateTotalProfit() / revenue) * 100;
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.customer) newErrors.customer = 'Customer is required';
    if (!formData.order_date) newErrors.order_date = 'Order date is required';
    if (lineItems.length === 0) newErrors.items = 'Add at least one item';

    lineItems.forEach((item, index) => {
      if (!item.product) newErrors[`item_${index}_product`] = 'Product required';
      if (!item.quantity || item.quantity <= 0) newErrors[`item_${index}_quantity`] = 'Valid quantity required';
      if (!item.unit_price || item.unit_price <= 0) newErrors[`item_${index}_price`] = 'Valid price required';
      if (item.unit_cost_snapshot === '' || item.unit_cost_snapshot < 0) {
        newErrors[`item_${index}_cost`] = 'Valid cost required';
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
      items: lineItems.map((item, idx) => ({
        product: parseInt(item.product),
        quantity: parseInt(item.quantity),
        unit_price: parseFloat(item.unit_price),
        unit_cost_snapshot: parseFloat(item.unit_cost_snapshot),
        display_order: idx,
      }))
    };

    try {
      if (isEdit) {
        await api.put(`/orders/orders/${id}/`, payload);
      } else {
        await api.post('/orders/orders/', payload);
      }
      navigate('/orders');
    } catch (err) {
      if (err.response?.data) {
        setErrors(err.response.data);
      } else {
        alert('Failed to save order');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const getProductById = (productId) => {
    return products.find(p => p.id === parseInt(productId));
  };

  if (loading) {
    return <div className="loading">Loading order...</div>;
  }

  const totalRevenue = calculateTotalRevenue();
  const totalCost = calculateTotalCost();
  const totalProfit = calculateTotalProfit();
  const margin = calculateMargin();

  return (
    <div className="order-form-page">
      <div className="form-header">
        <div>
          <h2>{isEdit ? '✏️ Edit Order' : '➕ Create New Order'}</h2>
          <p className="form-subtitle">
            {isEdit ? 'Update order details and items' : 'Enter customer order with line items'}
          </p>
        </div>
        <Link to="/orders" className="btn-secondary">← Back to Orders</Link>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-layout">
          <div className="form-main">
            {/* Customer & Date Info */}
            <div className="form-card">
              <h3>Order Information</h3>
              
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="customer">Customer <span className="required">*</span></label>
                  <select
                    id="customer"
                    name="customer"
                    value={formData.customer}
                    onChange={handleChange}
                    className={errors.customer ? 'error' : ''}
                  >
                    <option value="">Select Customer</option>
                    {customers.map(c => (
                      <option key={c.id} value={c.id}>
                        {c.name} - {c.mobile}
                      </option>
                    ))}
                  </select>
                  {errors.customer && <span className="error-text">{errors.customer}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="order_date">Order Date <span className="required">*</span></label>
                  <input
                    type="date"
                    id="order_date"
                    name="order_date"
                    value={formData.order_date}
                    onChange={handleChange}
                    className={errors.order_date ? 'error' : ''}
                  />
                  {errors.order_date && <span className="error-text">{errors.order_date}</span>}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="fulfillment_date">Fulfillment Date</label>
                  <input
                    type="date"
                    id="fulfillment_date"
                    name="fulfillment_date"
                    value={formData.fulfillment_date}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="order_type">Order Type</label>
                  <select
                    id="order_type"
                    name="order_type"
                    value={formData.order_type}
                    onChange={handleChange}
                  >
                    <option value="delivery">Delivery</option>
                    <option value="pickup">Pickup</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="status">Status</label>
                  <select
                    id="status"
                    name="status"
                    value={formData.status}
                    onChange={handleChange}
                  >
                    <option value="draft">Draft</option>
                    <option value="confirmed">Confirmed</option>
                    <option value="preparing">Preparing</option>
                    <option value="ready">Ready</option>
                    <option value="delivered">Delivered</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="payment_status">Payment Status</label>
                  <select
                    id="payment_status"
                    name="payment_status"
                    value={formData.payment_status}
                    onChange={handleChange}
                  >
                    <option value="pending">Pending</option>
                    <option value="partial">Partial</option>
                    <option value="paid">Paid</option>
                    <option value="refunded">Refunded</option>
                  </select>
                </div>
              </div>

              {formData.order_type === 'delivery' && (
                <>
                  <div className="form-group">
                    <label htmlFor="delivery_address">Delivery Address</label>
                    <textarea
                      id="delivery_address"
                      name="delivery_address"
                      value={formData.delivery_address}
                      onChange={handleChange}
                      rows="2"
                      placeholder="Leave empty to use customer's default address"
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="delivery_notes">Delivery Notes</label>
                    <textarea
                      id="delivery_notes"
                      name="delivery_notes"
                      value={formData.delivery_notes}
                      onChange={handleChange}
                      rows="2"
                      placeholder="Special delivery instructions"
                    />
                  </div>
                </>
              )}

              <div className="form-group">
                <label htmlFor="notes">Internal Notes</label>
                <textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows="2"
                  placeholder="Internal order notes"
                />
              </div>
            </div>

            {/* Line Items */}
            <div className="form-card">
              <div className="section-header">
                <h3>Order Items</h3>
                <button type="button" onClick={addLineItem} className="btn-secondary btn-sm">
                  + Add Item
                </button>
              </div>

              {errors.items && <div className="error-text">{errors.items}</div>}

              {lineItems.length === 0 ? (
                <div className="empty-items">
                  <p>No items yet. Add products to this order.</p>
                  <button type="button" onClick={addLineItem} className="btn-primary">
                    + Add First Item
                  </button>
                </div>
              ) : (
                <div className="line-items-list">
                  {lineItems.map((item, index) => {
                    const product = getProductById(item.product);
                    const lineTotal = calculateLineTotal(item);
                    const lineCost = calculateLineCost(item);
                    const lineProfit = lineTotal - lineCost;

                    return (
                      <div key={index} className="line-item">
                        <div className="item-header">
                          <span className="item-number">#{index + 1}</span>
                          <button
                            type="button"
                            onClick={() => removeLineItem(index)}
                            className="btn-remove"
                          >
                            🗑️ Remove
                          </button>
                        </div>

                        <div className="item-fields">
                          <div className="form-row">
                            <div className="form-group">
                              <label>Product *</label>
                              <select
                                value={item.product}
                                onChange={(e) => updateLineItem(index, 'product', e.target.value)}
                                className={errors[`item_${index}_product`] ? 'error' : ''}
                              >
                                <option value="">Select Product</option>
                                {products.map(p => (
                                  <option key={p.id} value={p.id}>
                                    {p.name} ({p.unit}) - ₹{p.selling_price}
                                  </option>
                                ))}
                              </select>
                              {errors[`item_${index}_product`] && (
                                <span className="error-text">{errors[`item_${index}_product`]}</span>
                              )}
                            </div>

                            <div className="form-group">
                              <label>Quantity *</label>
                              <input
                                type="number"
                                value={item.quantity}
                                onChange={(e) => updateLineItem(index, 'quantity', e.target.value)}
                                className={errors[`item_${index}_quantity`] ? 'error' : ''}
                                min="1"
                              />
                              {errors[`item_${index}_quantity`] && (
                                <span className="error-text">{errors[`item_${index}_quantity`]}</span>
                              )}
                            </div>
                          </div>

                          <div className="form-row">
                            <div className="form-group">
                              <label>Unit Price (₹) *</label>
                              <input
                                type="number"
                                value={item.unit_price}
                                onChange={(e) => updateLineItem(index, 'unit_price', e.target.value)}
                                className={errors[`item_${index}_price`] ? 'error' : ''}
                                step="0.01"
                                min="0.01"
                              />
                              {errors[`item_${index}_price`] && (
                                <span className="error-text">{errors[`item_${index}_price`]}</span>
                              )}
                            </div>

                            <div className="form-group">
                              <label>Unit Cost (₹) *</label>
                              <input
                                type="number"
                                value={item.unit_cost_snapshot}
                                onChange={(e) => updateLineItem(index, 'unit_cost_snapshot', e.target.value)}
                                className={errors[`item_${index}_cost`] ? 'error' : ''}
                                step="0.01"
                                min="0"
                              />
                              {errors[`item_${index}_cost`] && (
                                <span className="error-text">{errors[`item_${index}_cost`]}</span>
                              )}
                              <small className="hint">Cost snapshot at order time</small>
                            </div>
                          </div>

                          <div className="item-totals">
                            <div className="total-item">
                              <span>Line Total:</span>
                              <span className="value">₹{lineTotal.toFixed(2)}</span>
                            </div>
                            <div className="total-item">
                              <span>Line Cost:</span>
                              <span className="value">₹{lineCost.toFixed(2)}</span>
                            </div>
                            <div className="total-item profit">
                              <span>Line Profit:</span>
                              <span className="value">₹{lineProfit.toFixed(2)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Order Summary Sidebar */}
          <div className="form-sidebar">
            <div className="summary-card sticky">
              <h3>Order Summary</h3>
              
              <div className="summary-item">
                <span className="label">Items:</span>
                <span className="value">{lineItems.length}</span>
              </div>

              <div className="summary-item">
                <span className="label">Total Quantity:</span>
                <span className="value">
                  {lineItems.reduce((sum, item) => sum + (parseInt(item.quantity) || 0), 0)}
                </span>
              </div>

              <div className="summary-divider"></div>

              <div className="summary-item">
                <span className="label">Total Revenue:</span>
                <span className="value revenue">₹{totalRevenue.toFixed(2)}</span>
              </div>

              <div className="summary-item">
                <span className="label">Total Cost:</span>
                <span className="value cost">₹{totalCost.toFixed(2)}</span>
              </div>

              <div className="summary-item divider">
                <span className="label">Total Profit:</span>
                <span className={`value profit ${totalProfit < 0 ? 'negative' : ''}`}>
                  ₹{totalProfit.toFixed(2)}
                </span>
              </div>

              <div className="summary-item">
                <span className="label">Margin:</span>
                <span className={`value margin ${margin < 15 ? 'low' : margin < 30 ? 'medium' : 'high'}`}>
                  {margin.toFixed(1)}%
                </span>
              </div>

              {totalProfit < 0 && (
                <div className="warning-box">
                  ⚠️ Warning: Negative profit! Cost exceeds revenue.
                </div>
              )}

              <div className="summary-actions">
                <button type="submit" className="btn-primary" disabled={submitting}>
                  {submitting ? 'Saving...' : isEdit ? 'Update Order' : 'Create Order'}
                </button>
                <button
                  type="button"
                  onClick={() => navigate('/orders')}
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

export default OrderForm;

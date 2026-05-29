import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './GoogleSync.css';

function GoogleSync() {
  const [configs, setConfigs] = useState([]);
  const [syncHistory, setSyncHistory] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('configs');
  
  // Form state
  const [showForm, setShowForm] = useState(false);
  const [editingConfig, setEditingConfig] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    sheet_id: '',
    tab_name: 'Form Responses 1',
    field_mapping: {
      customer_name: 'B',
      mobile: 'C',
      apartment: '',
      block: '',
      product_name: 'D',
      quantity: 'E',
      size: '',
      order_date: 'A',
      notes: ''
    },
    default_product_id: '',
    default_order_type: 'delivery',
    write_back_enabled: false,
    order_number_column: '',
    status_column: ''
  });
  
  // Test connection state
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    fetchConfigs();
    fetchSyncHistory();
    fetchProducts();
  }, []);

  const fetchConfigs = async () => {
    try {
      const response = await api.get('/integrations/google-sheets/');
      setConfigs(response.data);
    } catch (err) {
      console.error('Failed to fetch configs:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSyncHistory = async () => {
    try {
      const response = await api.get('/integrations/google-sheets/sync-history/');
      setSyncHistory(response.data);
    } catch (err) {
      console.error('Failed to fetch sync history:', err);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await api.get('/integrations/google-sheets/products/');
      setProducts(response.data);
    } catch (err) {
      console.error('Failed to fetch products:', err);
    }
  };

  const handleTestConnection = async () => {
    if (!formData.sheet_id) {
      setError('Please enter a Sheet ID');
      return;
    }
    
    setTesting(true);
    setTestResult(null);
    setError(null);
    
    try {
      const response = await api.post('/integrations/google-sheets/test-connection/', {
        sheet_id: formData.sheet_id,
        tab_name: formData.tab_name
      });
      setTestResult(response.data);
    } catch (err) {
      setTestResult({
        success: false,
        message: err.response?.data?.message || 'Connection failed'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    try {
      if (editingConfig) {
        await api.put(`/integrations/google-sheets/${editingConfig.id}/`, formData);
      } else {
        await api.post('/integrations/google-sheets/', formData);
      }
      
      setShowForm(false);
      setEditingConfig(null);
      resetForm();
      fetchConfigs();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save configuration');
    }
  };

  const handleEdit = (config) => {
    setEditingConfig(config);
    setFormData({
      name: config.name,
      sheet_id: config.sheet_id,
      tab_name: config.tab_name,
      field_mapping: config.field_mapping || {},
      default_product_id: config.default_product_id || '',
      default_order_type: config.default_order_type || 'delivery',
      write_back_enabled: config.write_back_enabled || false,
      order_number_column: config.order_number_column || '',
      status_column: config.status_column || ''
    });
    setShowForm(true);
    setTestResult(null);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this configuration?')) {
      return;
    }
    
    try {
      await api.delete(`/integrations/google-sheets/${id}/`);
      fetchConfigs();
    } catch (err) {
      setError('Failed to delete configuration');
    }
  };

  const handleSync = async (configId) => {
    setSyncing(configId);
    setError(null);
    
    try {
      const response = await api.post(`/integrations/google-sheets/${configId}/sync/`);
      
      // Show result
      const result = response.data;
      alert(`Sync Complete!\n\nProcessed: ${result.rows_processed}\nCreated: ${result.rows_created}\nSkipped: ${result.rows_skipped}\nFailed: ${result.rows_failed}`);
      
      fetchConfigs();
      fetchSyncHistory();
    } catch (err) {
      setError(err.response?.data?.error || 'Sync failed');
    } finally {
      setSyncing(null);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      sheet_id: '',
      tab_name: 'Form Responses 1',
      field_mapping: {
        customer_name: 'B',
        mobile: 'C',
        apartment: '',
        block: '',
        product_name: 'D',
        quantity: 'E',
        order_date: 'A',
        notes: ''
      },
      default_product_id: '',
      default_order_type: 'delivery',
      write_back_enabled: false,
      order_number_column: '',
      status_column: ''
    });
    setTestResult(null);
  };

  const updateFieldMapping = (field, value) => {
    setFormData({
      ...formData,
      field_mapping: {
        ...formData.field_mapping,
        [field]: value.toUpperCase()
      }
    });
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString();
  };

  const getStatusBadge = (status) => {
    const colors = {
      'completed': 'badge-green',
      'failed': 'badge-red',
      'running': 'badge-yellow',
      'pending': 'badge-gray'
    };
    return <span className={`status-badge ${colors[status] || 'badge-gray'}`}>{status}</span>;
  };

  return (
    <div className="google-sync-page">
      <div className="page-header">
        <h1>📊 Google Sheets Sync</h1>
        <p className="page-subtitle">Import orders from Google Forms responses</p>
      </div>

      <div className="sync-tabs">
        <button 
          className={`tab-btn ${activeTab === 'configs' ? 'active' : ''}`}
          onClick={() => setActiveTab('configs')}
        >
          ⚙️ Configurations
        </button>
        <button 
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📋 Sync History
        </button>
        <button 
          className={`tab-btn ${activeTab === 'help' ? 'active' : ''}`}
          onClick={() => setActiveTab('help')}
        >
          ❓ Setup Guide
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {activeTab === 'configs' && (
        <div className="configs-section">
          {!showForm ? (
            <>
              <div className="section-header">
                <h3>Sheet Configurations</h3>
                <button className="btn btn-primary" onClick={() => setShowForm(true)}>
                  ➕ Add Configuration
                </button>
              </div>

              {loading ? (
                <p>Loading...</p>
              ) : configs.length === 0 ? (
                <div className="empty-state">
                  <p>No Google Sheet configurations yet.</p>
                  <p>Click "Add Configuration" to connect your first Google Form.</p>
                </div>
              ) : (
                <div className="config-cards">
                  {configs.map(config => (
                    <div key={config.id} className={`config-card ${config.is_active ? '' : 'inactive'}`}>
                      <div className="config-header">
                        <h4>{config.name}</h4>
                        {!config.is_active && <span className="badge-gray">Inactive</span>}
                      </div>
                      <div className="config-details">
                        <p><strong>Sheet ID:</strong> {config.sheet_id.substring(0, 20)}...</p>
                        <p><strong>Tab:</strong> {config.tab_name}</p>
                        {config.last_sync && (
                          <p>
                            <strong>Last Sync:</strong> {formatDate(config.last_sync.started_at)}
                            <br/>
                            <span className="sync-result">
                              {config.last_sync.rows_created} orders created
                            </span>
                          </p>
                        )}
                      </div>
                      <div className="config-actions">
                        <button 
                          className="btn btn-success"
                          onClick={() => handleSync(config.id)}
                          disabled={syncing === config.id}
                        >
                          {syncing === config.id ? '⏳ Syncing...' : '🔄 Sync Now'}
                        </button>
                        <button className="btn btn-secondary" onClick={() => handleEdit(config)}>
                          ✏️ Edit
                        </button>
                        <button className="btn btn-danger" onClick={() => handleDelete(config.id)}>
                          🗑️
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="config-form">
              <h3>{editingConfig ? 'Edit Configuration' : 'Add Configuration'}</h3>
              
              <form onSubmit={handleSubmit}>
                <div className="form-section">
                  <h4>Basic Settings</h4>
                  
                  <div className="form-group">
                    <label>Configuration Name *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      placeholder="e.g., Mango Pickle Orders"
                      required
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Google Sheet ID *</label>
                      <input
                        type="text"
                        value={formData.sheet_id}
                        onChange={(e) => setFormData({...formData, sheet_id: e.target.value})}
                        placeholder="From sheet URL: docs.google.com/spreadsheets/d/[SHEET_ID]/edit"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Tab Name</label>
                      <input
                        type="text"
                        value={formData.tab_name}
                        onChange={(e) => setFormData({...formData, tab_name: e.target.value})}
                        placeholder="Form Responses 1"
                      />
                    </div>
                  </div>

                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    onClick={handleTestConnection}
                    disabled={testing}
                  >
                    {testing ? '⏳ Testing...' : '🔗 Test Connection'}
                  </button>

                  {testResult && (
                    <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
                      <p>{testResult.message}</p>
                      {testResult.headers && testResult.headers.length > 0 && (
                        <div className="headers-preview">
                          <strong>Detected Columns:</strong>
                          <div className="column-list">
                            {testResult.headers.map((h, i) => (
                              <span key={i} className="column-tag">
                                {String.fromCharCode(65 + i)}: {h}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="form-section">
                  <h4>Column Mapping</h4>
                  <p className="help-text">Map sheet columns (A, B, C...) to order fields</p>
                  
                  <div className="mapping-grid">
                    <div className="form-group">
                      <label>Customer Name Column</label>
                      <input
                        type="text"
                        value={formData.field_mapping.customer_name || ''}
                        onChange={(e) => updateFieldMapping('customer_name', e.target.value)}
                        placeholder="e.g., B"
                        maxLength={2}
                      />
                    </div>
                    <div className="form-group">
                      <label>Mobile Column *</label>
                      <input
                        type="text"
                        value={formData.field_mapping.mobile || ''}
                        onChange={(e) => updateFieldMapping('mobile', e.target.value)}
                        placeholder="e.g., C"
                        maxLength={2}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Product Column</label>
                      <input
                        type="text"
                        value={formData.field_mapping.product_name || ''}
                        onChange={(e) => updateFieldMapping('product_name', e.target.value)}
                        placeholder="e.g., D"
                        maxLength={2}
                      />
                    </div>
                    <div className="form-group">
                      <label>Quantity Column</label>
                      <input
                        type="text"
                        value={formData.field_mapping.quantity || ''}
                        onChange={(e) => updateFieldMapping('quantity', e.target.value)}
                        placeholder="e.g., E"
                        maxLength={2}
                      />
                    </div>
                    <div className="form-group">
                      <label>Order Date Column</label>
                      <input
                        type="text"
                        value={formData.field_mapping.order_date || ''}
                        onChange={(e) => updateFieldMapping('order_date', e.target.value)}
                        placeholder="e.g., A (timestamp)"
                        maxLength={2}
                      />
                    </div>
                    <div className="form-group">
                      <label>Apartment Column</label>
                      <input
                        type="text"
                        value={formData.field_mapping.apartment || ''}
                        onChange={(e) => updateFieldMapping('apartment', e.target.value)}
                        placeholder="e.g., F"
                        maxLength={2}
                      />
                    </div>
                    <div className="form-group">
                      <label>Notes Column</label>
                      <input
                        type="text"
                        value={formData.field_mapping.notes || ''}
                        onChange={(e) => updateFieldMapping('notes', e.target.value)}
                        placeholder="e.g., F (comments)"
                        maxLength={2}
                      />
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h4>Default Values</h4>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label>Default Product (if not in sheet)</label>
                      <select
                        value={formData.default_product_id}
                        onChange={(e) => setFormData({...formData, default_product_id: e.target.value})}
                      >
                        <option value="">-- Select Product --</option>
                        {products.map(p => (
                          <option key={p.id} value={p.id}>
                            {p.name} ({p.unit}) - ₹{p.selling_price}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Default Order Type</label>
                      <select
                        value={formData.default_order_type}
                        onChange={(e) => setFormData({...formData, default_order_type: e.target.value})}
                      >
                        <option value="delivery">Delivery</option>
                        <option value="pickup">Pickup</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h4>Write-Back (Optional)</h4>
                  <p className="help-text">Write order number and status back to the sheet</p>
                  
                  <div className="form-group checkbox">
                    <label>
                      <input
                        type="checkbox"
                        checked={formData.write_back_enabled}
                        onChange={(e) => setFormData({...formData, write_back_enabled: e.target.checked})}
                      />
                      Enable write-back
                    </label>
                  </div>

                  {formData.write_back_enabled && (
                    <div className="form-row">
                      <div className="form-group">
                        <label>Order Number Column</label>
                        <input
                          type="text"
                          value={formData.order_number_column}
                          onChange={(e) => setFormData({...formData, order_number_column: e.target.value.toUpperCase()})}
                          placeholder="e.g., G"
                          maxLength={2}
                        />
                      </div>
                      <div className="form-group">
                        <label>Status Column</label>
                        <input
                          type="text"
                          value={formData.status_column}
                          onChange={(e) => setFormData({...formData, status_column: e.target.value.toUpperCase()})}
                          placeholder="e.g., H"
                          maxLength={2}
                        />
                      </div>
                    </div>
                  )}
                </div>

                <div className="form-actions">
                  <button type="submit" className="btn btn-primary">
                    {editingConfig ? '💾 Update' : '➕ Create'}
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-secondary"
                    onClick={() => {
                      setShowForm(false);
                      setEditingConfig(null);
                      resetForm();
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}

      {activeTab === 'history' && (
        <div className="history-section">
          <h3>Sync History</h3>
          
          {syncHistory.length === 0 ? (
            <p className="empty-state">No sync history yet</p>
          ) : (
            <table className="history-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Configuration</th>
                  <th>Status</th>
                  <th>Processed</th>
                  <th>Created</th>
                  <th>Skipped</th>
                  <th>Failed</th>
                  <th>By</th>
                </tr>
              </thead>
              <tbody>
                {syncHistory.map(log => (
                  <tr key={log.id}>
                    <td>{formatDate(log.started_at)}</td>
                    <td>{log.config_name}</td>
                    <td>{getStatusBadge(log.status)}</td>
                    <td>{log.rows_processed}</td>
                    <td className="success-cell">{log.rows_created}</td>
                    <td>{log.rows_skipped}</td>
                    <td className="failed-cell">{log.rows_failed}</td>
                    <td>{log.synced_by_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {activeTab === 'help' && (
        <div className="help-section">
          <h3>Setup Guide</h3>
          
          <div className="help-card">
            <h4>1. Create a Google Form</h4>
            <p>Create a Google Form with fields for:</p>
            <ul>
              <li>Customer Name</li>
              <li>Mobile Number (required)</li>
              <li>Product/Item selection</li>
              <li>Quantity</li>
              <li>Apartment/Address (optional)</li>
            </ul>
          </div>

          <div className="help-card">
            <h4>2. Link to Google Sheets</h4>
            <p>In your Google Form, click the "Responses" tab and then the green Sheets icon to create a linked spreadsheet.</p>
          </div>

          <div className="help-card">
            <h4>3. Share with Service Account</h4>
            <p>Share the Google Sheet with the service account email:</p>
            <code>your-service-account@your-project.iam.gserviceaccount.com</code>
            <p>(Ask your administrator for the exact email)</p>
          </div>

          <div className="help-card">
            <h4>4. Get Sheet ID</h4>
            <p>From the sheet URL, copy the ID between /d/ and /edit:</p>
            <code>docs.google.com/spreadsheets/d/<strong>[SHEET_ID]</strong>/edit</code>
          </div>

          <div className="help-card">
            <h4>5. Configure Mapping</h4>
            <p>Use "Test Connection" to see your column letters, then map them to order fields.</p>
            <p>Typical mapping for a Google Form response:</p>
            <ul>
              <li><strong>A</strong> = Timestamp (Order Date)</li>
              <li><strong>B</strong> = Customer Name</li>
              <li><strong>C</strong> = Mobile Number</li>
              <li><strong>D</strong> = Product Selection</li>
              <li><strong>E</strong> = Quantity</li>
            </ul>
          </div>

          <div className="help-card">
            <h4>6. Sync Orders</h4>
            <p>Click "Sync Now" to import new form responses as orders. Already-synced rows will be skipped to prevent duplicates.</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default GoogleSync;

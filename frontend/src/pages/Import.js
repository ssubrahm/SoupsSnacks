import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Import.css';

function Import() {
  const [importType, setImportType] = useState('customers');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [template, setTemplate] = useState(null);
  const [activeTab, setActiveTab] = useState('import');

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    fetchTemplate();
  }, [importType]);

  const fetchHistory = async () => {
    try {
      const response = await api.get('/imports/history/');
      setHistory(response.data);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  };

  const fetchTemplate = async () => {
    try {
      const response = await api.get(`/imports/template/${importType}/`);
      setTemplate(response.data);
    } catch (err) {
      console.error('Failed to fetch template:', err);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  const handlePreview = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    setPreview(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('import_type', importType);

      const response = await api.post('/imports/preview/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setPreview(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to preview file');
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!file || !preview) {
      setError('Please preview the file first');
      return;
    }

    if (preview.valid_rows === 0) {
      setError('No valid rows to import');
      return;
    }

    setImporting(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('import_type', importType);
      formData.append('import_mode', 'valid_only');

      const response = await api.post('/imports/confirm/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setResult(response.data);
      setPreview(null);
      setFile(null);
      
      // Reset file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';
      
      // Refresh history
      fetchHistory();
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.message || 'Import failed');
      if (err.response?.data?.errors) {
        setResult({ success: false, errors: err.response.data.errors });
      }
    } finally {
      setImporting(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
  };

  const downloadTemplate = () => {
    if (!template) return;

    const headers = [...template.required_fields, ...template.optional_fields];
    const rows = template.sample_data.map(row => 
      headers.map(h => row[h] || '').join(',')
    );
    
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${importType}_template.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString();
  };

  const getStatusBadge = (status) => {
    const colors = {
      'completed': 'badge-green',
      'failed': 'badge-red',
      'processing': 'badge-yellow',
      'pending': 'badge-gray'
    };
    return <span className={`status-badge ${colors[status] || 'badge-gray'}`}>{status}</span>;
  };

  return (
    <div className="import-page">
      <div className="page-header">
        <h1>📥 Data Import</h1>
        <p className="page-subtitle">Import customers, products, orders, and payments from CSV or Excel</p>
      </div>

      <div className="import-tabs">
        <button 
          className={`tab-btn ${activeTab === 'import' ? 'active' : ''}`}
          onClick={() => setActiveTab('import')}
        >
          📤 Import Data
        </button>
        <button 
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📋 Import History
        </button>
        <button 
          className={`tab-btn ${activeTab === 'templates' ? 'active' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          📄 Templates
        </button>
      </div>

      {activeTab === 'import' && (
        <div className="import-section">
          {/* Step 1: Select Type and File */}
          <div className="import-card">
            <h3>Step 1: Select Import Type and File</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label>Import Type</label>
                <select 
                  value={importType} 
                  onChange={(e) => {
                    setImportType(e.target.value);
                    handleReset();
                  }}
                  disabled={loading || importing}
                >
                  <option value="customers">👥 Customers</option>
                  <option value="products">🍛 Products</option>
                  <option value="orders">🥘 Orders</option>
                  <option value="payments">💰 Payments</option>
                </select>
              </div>

              <div className="form-group">
                <label>File (CSV or Excel)</label>
                <input
                  id="file-input"
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileChange}
                  disabled={loading || importing}
                />
              </div>
            </div>

            {file && (
              <div className="file-info">
                📎 Selected: <strong>{file.name}</strong> ({(file.size / 1024).toFixed(1)} KB)
              </div>
            )}

            <div className="button-row">
              <button 
                className="btn btn-primary"
                onClick={handlePreview}
                disabled={!file || loading || importing}
              >
                {loading ? '⏳ Processing...' : '👁️ Preview'}
              </button>
              <button 
                className="btn btn-secondary"
                onClick={downloadTemplate}
                disabled={!template}
              >
                📥 Download Template
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-card">
              ❌ {error}
            </div>
          )}

          {/* Step 2: Preview */}
          {preview && (
            <div className="import-card">
              <h3>Step 2: Review Preview</h3>
              
              <div className="preview-summary">
                <div className="summary-item">
                  <span className="summary-value">{preview.total_rows}</span>
                  <span className="summary-label">Total Rows</span>
                </div>
                <div className="summary-item valid">
                  <span className="summary-value">{preview.valid_rows}</span>
                  <span className="summary-label">Valid Rows</span>
                </div>
                <div className="summary-item invalid">
                  <span className="summary-value">{preview.invalid_rows}</span>
                  <span className="summary-label">Invalid Rows</span>
                </div>
              </div>

              {preview.errors.length > 0 && (
                <div className="errors-section">
                  <h4>⚠️ Validation Errors ({preview.errors.length}{preview.has_more_errors ? '+' : ''})</h4>
                  <ul className="error-list">
                    {preview.errors.map((err, i) => (
                      <li key={i}>{err}</li>
                    ))}
                  </ul>
                </div>
              )}

              {preview.preview_data.length > 0 && (
                <div className="preview-table-section">
                  <h4>📋 Data Preview (first 10 rows)</h4>
                  <div className="table-wrapper">
                    <table className="preview-table">
                      <thead>
                        <tr>
                          {preview.headers.map((h, i) => (
                            <th key={i}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {preview.preview_data.map((row, i) => (
                          <tr key={i}>
                            {preview.headers.map((h, j) => (
                              <td key={j}>{row[h] || '-'}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <div className="button-row">
                <button 
                  className="btn btn-success"
                  onClick={handleImport}
                  disabled={preview.valid_rows === 0 || importing}
                >
                  {importing ? '⏳ Importing...' : `✅ Import ${preview.valid_rows} Valid Rows`}
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={handleReset}
                  disabled={importing}
                >
                  🔄 Start Over
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Result */}
          {result && (
            <div className={`import-card ${result.success ? 'success' : 'error'}`}>
              <h3>{result.success ? '✅ Import Successful!' : '❌ Import Had Issues'}</h3>
              
              {result.success && (
                <div className="result-summary">
                  <p>Successfully imported <strong>{result.imported}</strong> rows.</p>
                  {result.failed > 0 && (
                    <p className="warning">{result.failed} rows were skipped due to errors.</p>
                  )}
                </div>
              )}

              {result.errors && result.errors.length > 0 && (
                <div className="errors-section">
                  <h4>Errors:</h4>
                  <ul className="error-list">
                    {result.errors.slice(0, 20).map((err, i) => (
                      <li key={i}>{err}</li>
                    ))}
                  </ul>
                </div>
              )}

              <button 
                className="btn btn-primary"
                onClick={handleReset}
              >
                📤 Import More Data
              </button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'history' && (
        <div className="history-section">
          <h3>📋 Import History</h3>
          
          {history.length === 0 ? (
            <p className="no-data">No imports yet</p>
          ) : (
            <table className="history-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>File</th>
                  <th>Status</th>
                  <th>Total</th>
                  <th>Success</th>
                  <th>Failed</th>
                  <th>By</th>
                </tr>
              </thead>
              <tbody>
                {history.map(log => (
                  <tr key={log.id}>
                    <td>{formatDate(log.created_at)}</td>
                    <td className="type-cell">{log.import_type}</td>
                    <td className="file-cell" title={log.file_name}>{log.file_name}</td>
                    <td>{getStatusBadge(log.status)}</td>
                    <td>{log.total_rows}</td>
                    <td className="success-cell">{log.successful_rows}</td>
                    <td className="failed-cell">{log.failed_rows}</td>
                    <td>{log.imported_by_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="templates-section">
          <h3>📄 Import Templates</h3>
          
          <div className="template-cards">
            {['customers', 'products', 'orders', 'payments'].map(type => (
              <div key={type} className="template-card">
                <h4>{type.charAt(0).toUpperCase() + type.slice(1)}</h4>
                <p className="template-desc">
                  {type === 'customers' && 'Import customer contact information'}
                  {type === 'products' && 'Import product catalog with pricing'}
                  {type === 'orders' && 'Import orders with line items'}
                  {type === 'payments' && 'Import payment records'}
                </p>
                <button 
                  className="btn btn-secondary"
                  onClick={() => {
                    setImportType(type);
                    setTimeout(downloadTemplate, 100);
                  }}
                >
                  📥 Download {type}.csv
                </button>
              </div>
            ))}
          </div>

          {template && (
            <div className="template-details">
              <h4>Template Details: {importType}</h4>
              
              <div className="fields-section">
                <div className="field-group">
                  <h5>Required Fields</h5>
                  <ul>
                    {template.required_fields.map(f => (
                      <li key={f} className="required">{f}</li>
                    ))}
                  </ul>
                </div>
                <div className="field-group">
                  <h5>Optional Fields</h5>
                  <ul>
                    {template.optional_fields.map(f => (
                      <li key={f}>{f}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {template.categories && (
                <div className="info-section">
                  <h5>Valid Categories</h5>
                  <p>{template.categories.join(', ')}</p>
                </div>
              )}

              {template.payment_methods && (
                <div className="info-section">
                  <h5>Valid Payment Methods</h5>
                  <p>{template.payment_methods.join(', ')}</p>
                </div>
              )}

              {template.notes && (
                <div className="info-section">
                  <h5>Notes</h5>
                  <p>{template.notes}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Import;

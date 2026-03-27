import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../services/api';
import './Reports.css';

const Reports = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'sales');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [filters, setFilters] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    sort_by: 'total_spent',
    inactive_days: 30,
  });

  useEffect(() => {
    fetchReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, filters.start_date, filters.end_date]);

  const fetchReport = async () => {
    setLoading(true);
    try {
      let endpoint = '/reports/sales/';
      let params = {
        start_date: filters.start_date,
        end_date: filters.end_date,
      };

      switch (activeTab) {
        case 'customers':
          endpoint = '/reports/customers/';
          params.sort_by = filters.sort_by;
          break;
        case 'products':
          endpoint = '/reports/products/';
          params.sort_by = filters.sort_by;
          break;
        case 'unpaid':
          endpoint = '/reports/unpaid/';
          params = {};
          break;
        case 'inactive':
          endpoint = '/reports/inactive-customers/';
          params = { days: filters.inactive_days };
          break;
        case 'profitability':
          endpoint = '/reports/order-profitability/';
          break;
        default:
          endpoint = '/reports/sales/';
      }

      const response = await api.get(endpoint, { params });
      setData(response.data);
    } catch (err) {
      console.error('Report error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (type) => {
    try {
      const endpoints = {
        sales: '/reports/export/sales/',
        customers: '/reports/export/customers/',
        products: '/reports/export/products/',
        unpaid: '/reports/export/unpaid/',
      };

      const response = await api.get(endpoints[type] || endpoints.sales, {
        params: { start_date: filters.start_date, end_date: filters.end_date },
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${type}_report_${filters.start_date}_${filters.end_date}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Export failed');
    }
  };

  const formatCurrency = (amount) => `₹${parseFloat(amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const changeTab = (tab) => {
    setActiveTab(tab);
    setSearchParams({ tab });
  };

  const renderSalesReport = () => (
    <div className="report-content">
      {data?.summary && (
        <div className="summary-cards">
          <div className="summary-card">
            <div className="summary-value">{data.summary.total_orders}</div>
            <div className="summary-label">Total Orders</div>
          </div>
          <div className="summary-card">
            <div className="summary-value">{formatCurrency(data.summary.total_revenue)}</div>
            <div className="summary-label">Total Revenue</div>
          </div>
          <div className="summary-card">
            <div className="summary-value">{formatCurrency(data.summary.total_profit)}</div>
            <div className="summary-label">Total Profit</div>
          </div>
          <div className="summary-card">
            <div className="summary-value">{formatCurrency(data.summary.avg_order_value)}</div>
            <div className="summary-label">Avg Order Value</div>
          </div>
        </div>
      )}

      {data?.data?.length > 0 && (
        <table className="report-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Orders</th>
              <th>Revenue</th>
              <th>Profit</th>
            </tr>
          </thead>
          <tbody>
            {data.data.map((row, idx) => (
              <tr key={idx}>
                <td>{row.period}</td>
                <td>{row.orders}</td>
                <td>{formatCurrency(row.revenue)}</td>
                <td>{formatCurrency(row.profit)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );

  const renderCustomerReport = () => (
    <div className="report-content">
      <div className="report-meta">
        <p>Total Customers: <strong>{data?.customer_count || 0}</strong></p>
        <p>Total Revenue: <strong>{formatCurrency(data?.total_revenue)}</strong></p>
      </div>

      {data?.data?.length > 0 && (
        <table className="report-table">
          <thead>
            <tr>
              <th>Customer</th>
              <th>Apartment</th>
              <th>Orders</th>
              <th>Total Spent</th>
              <th>Avg Order</th>
              <th>Share %</th>
              <th>Last Order</th>
            </tr>
          </thead>
          <tbody>
            {data.data.map((row, idx) => (
              <tr key={idx}>
                <td>
                  <div className="customer-cell">
                    <span className="customer-name">{row.customer_name}</span>
                    <span className="customer-mobile">{row.mobile}</span>
                  </div>
                </td>
                <td>{row.apartment || '-'} {row.block || ''}</td>
                <td>{row.order_count}</td>
                <td className="amount">{formatCurrency(row.total_spent)}</td>
                <td>{formatCurrency(row.avg_order_value)}</td>
                <td>
                  <div className="share-bar">
                    <div className="share-fill" style={{ width: `${row.percentage_share}%` }}></div>
                    <span>{row.percentage_share}%</span>
                  </div>
                </td>
                <td>{row.last_order || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );

  const renderProductReport = () => (
    <div className="report-content">
      <div className="report-meta">
        <p>Products Sold: <strong>{data?.product_count || 0}</strong></p>
      </div>

      {data?.data?.length > 0 && (
        <table className="report-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Category</th>
              <th>Qty Sold</th>
              <th>Revenue</th>
              <th>Cost</th>
              <th>Profit</th>
              <th>Margin %</th>
            </tr>
          </thead>
          <tbody>
            {data.data.map((row, idx) => (
              <tr key={idx}>
                <td>
                  <div className="product-cell">
                    <span className="product-name">{row.product_name}</span>
                    <span className="product-size">{row.unit_size}</span>
                  </div>
                </td>
                <td><span className="category-badge">{row.category}</span></td>
                <td className="qty">{row.total_qty}</td>
                <td className="amount">{formatCurrency(row.total_revenue)}</td>
                <td>{formatCurrency(row.total_cost)}</td>
                <td className="profit">{formatCurrency(row.total_profit)}</td>
                <td>
                  <span className={`margin ${row.margin_percent >= 30 ? 'good' : row.margin_percent >= 20 ? 'ok' : 'low'}`}>
                    {row.margin_percent}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );

  const renderUnpaidReport = () => (
    <div className="report-content">
      <div className="summary-cards warning">
        <div className="summary-card">
          <div className="summary-value">{data?.total_orders || 0}</div>
          <div className="summary-label">Unpaid Orders</div>
        </div>
        <div className="summary-card highlight">
          <div className="summary-value">{formatCurrency(data?.total_outstanding)}</div>
          <div className="summary-label">Total Outstanding</div>
        </div>
      </div>

      {data?.data?.length > 0 && (
        <table className="report-table">
          <thead>
            <tr>
              <th>Order #</th>
              <th>Date</th>
              <th>Customer</th>
              <th>Mobile</th>
              <th>Order Total</th>
              <th>Paid</th>
              <th>Outstanding</th>
              <th>Days Old</th>
            </tr>
          </thead>
          <tbody>
            {data.data.map((row, idx) => (
              <tr key={idx} className={row.days_old > 30 ? 'overdue' : ''}>
                <td><a href={`/orders/${row.order_id}`}>{row.order_number}</a></td>
                <td>{row.order_date}</td>
                <td>{row.customer_name}</td>
                <td>{row.customer_mobile}</td>
                <td>{formatCurrency(row.order_total)}</td>
                <td>{formatCurrency(row.amount_paid)}</td>
                <td className="outstanding">{formatCurrency(row.outstanding)}</td>
                <td>
                  <span className={`days-badge ${row.days_old > 30 ? 'old' : row.days_old > 7 ? 'medium' : 'recent'}`}>
                    {row.days_old} days
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );

  const renderInactiveReport = () => (
    <div className="report-content">
      <div className="filter-row">
        <label>
          Inactive for more than:
          <select 
            value={filters.inactive_days} 
            onChange={(e) => {
              setFilters({...filters, inactive_days: e.target.value});
              setTimeout(fetchReport, 100);
            }}
          >
            <option value="7">7 days</option>
            <option value="14">14 days</option>
            <option value="30">30 days</option>
            <option value="60">60 days</option>
            <option value="90">90 days</option>
          </select>
        </label>
      </div>

      <div className="report-meta">
        <p>Inactive Customers: <strong>{data?.inactive_count || 0}</strong></p>
      </div>

      {data?.data?.length > 0 && (
        <table className="report-table">
          <thead>
            <tr>
              <th>Customer</th>
              <th>Mobile</th>
              <th>Apartment</th>
              <th>Last Order</th>
              <th>Days Since</th>
              <th>Total Spent</th>
            </tr>
          </thead>
          <tbody>
            {data.data.map((row, idx) => (
              <tr key={idx}>
                <td>{row.customer_name}</td>
                <td>{row.mobile}</td>
                <td>{row.apartment || '-'} {row.block || ''}</td>
                <td>{row.last_order_date || 'Never'}</td>
                <td>
                  <span className="days-badge old">
                    {row.days_since_order ? `${row.days_since_order} days` : 'Never ordered'}
                  </span>
                </td>
                <td>{formatCurrency(row.total_spent)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );

  const renderProfitabilityReport = () => (
    <div className="report-content">
      {data?.summary && (
        <div className="summary-cards">
          <div className="summary-card">
            <div className="summary-value">{data.summary.total_orders}</div>
            <div className="summary-label">Orders</div>
          </div>
          <div className="summary-card">
            <div className="summary-value">{formatCurrency(data.summary.total_revenue)}</div>
            <div className="summary-label">Revenue</div>
          </div>
          <div className="summary-card">
            <div className="summary-value">{formatCurrency(data.summary.total_profit)}</div>
            <div className="summary-label">Profit</div>
          </div>
          <div className="summary-card">
            <div className="summary-value">{data.summary.avg_margin}%</div>
            <div className="summary-label">Avg Margin</div>
          </div>
        </div>
      )}

      {data?.data?.length > 0 && (
        <table className="report-table">
          <thead>
            <tr>
              <th>Order #</th>
              <th>Date</th>
              <th>Customer</th>
              <th>Items</th>
              <th>Revenue</th>
              <th>Cost</th>
              <th>Profit</th>
              <th>Margin %</th>
            </tr>
          </thead>
          <tbody>
            {data.data.map((row, idx) => (
              <tr key={idx}>
                <td><a href={`/orders/${row.order_id}`}>{row.order_number}</a></td>
                <td>{row.order_date}</td>
                <td>{row.customer_name}</td>
                <td>{row.item_count}</td>
                <td className="amount">{formatCurrency(row.total_revenue)}</td>
                <td>{formatCurrency(row.total_cost)}</td>
                <td className="profit">{formatCurrency(row.total_profit)}</td>
                <td>
                  <span className={`margin ${row.margin_percent >= 30 ? 'good' : row.margin_percent >= 20 ? 'ok' : 'low'}`}>
                    {row.margin_percent}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );

  return (
    <div className="reports-page">
      <div className="page-header">
        <h1>📊 Reports</h1>
        <p className="subtitle">Business insights and analytics</p>
      </div>

      {/* Tabs */}
      <div className="report-tabs">
        <button className={activeTab === 'sales' ? 'active' : ''} onClick={() => changeTab('sales')}>
          📈 Sales
        </button>
        <button className={activeTab === 'customers' ? 'active' : ''} onClick={() => changeTab('customers')}>
          👥 Customers
        </button>
        <button className={activeTab === 'products' ? 'active' : ''} onClick={() => changeTab('products')}>
          🍛 Products
        </button>
        <button className={activeTab === 'profitability' ? 'active' : ''} onClick={() => changeTab('profitability')}>
          💰 Profitability
        </button>
        <button className={activeTab === 'unpaid' ? 'active' : ''} onClick={() => changeTab('unpaid')}>
          ⚠️ Unpaid
        </button>
        <button className={activeTab === 'inactive' ? 'active' : ''} onClick={() => changeTab('inactive')}>
          😴 Inactive
        </button>
      </div>

      {/* Filters */}
      {activeTab !== 'unpaid' && activeTab !== 'inactive' && (
        <div className="report-filters">
          <div className="filter-group">
            <label>From:</label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => setFilters({...filters, start_date: e.target.value})}
            />
          </div>
          <div className="filter-group">
            <label>To:</label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => setFilters({...filters, end_date: e.target.value})}
            />
          </div>
          <button className="btn-filter" onClick={fetchReport}>Apply</button>
          {['sales', 'customers', 'products', 'unpaid'].includes(activeTab) && (
            <button className="btn-export" onClick={() => handleExport(activeTab)}>
              📥 Export CSV
            </button>
          )}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading report...</p>
        </div>
      ) : (
        <>
          {activeTab === 'sales' && renderSalesReport()}
          {activeTab === 'customers' && renderCustomerReport()}
          {activeTab === 'products' && renderProductReport()}
          {activeTab === 'unpaid' && renderUnpaidReport()}
          {activeTab === 'inactive' && renderInactiveReport()}
          {activeTab === 'profitability' && renderProfitabilityReport()}
        </>
      )}
    </div>
  );
};

export default Reports;

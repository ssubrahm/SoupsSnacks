import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './CustomerAnalytics.css';

function CustomerAnalytics() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [customerList, setCustomerList] = useState(null);
  const [repeatData, setRepeatData] = useState(null);
  const [frequencyData, setFrequencyData] = useState(null);
  const [recencyData, setRecencyData] = useState(null);
  const [ltvData, setLtvData] = useState(null);
  const [cohortData, setCohortData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filters for customer list
  const [loyaltyFilter, setLoyaltyFilter] = useState('');
  const [recencyFilter, setRecencyFilter] = useState('');
  const [sortBy, setSortBy] = useState('total_revenue');

  useEffect(() => {
    fetchDashboard();
  }, []);

  useEffect(() => {
    if (activeTab === 'customers') {
      fetchCustomerList();
    } else if (activeTab === 'repeat') {
      fetchRepeatData();
    } else if (activeTab === 'frequency') {
      fetchFrequencyData();
    } else if (activeTab === 'recency') {
      fetchRecencyData();
    } else if (activeTab === 'ltv') {
      fetchLtvData();
    } else if (activeTab === 'cohorts') {
      fetchCohortData();
    }
  }, [activeTab, loyaltyFilter, recencyFilter, sortBy]);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/reports/loyalty/dashboard/');
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomerList = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (loyaltyFilter) params.append('loyalty_segment', loyaltyFilter);
      if (recencyFilter) params.append('recency_status', recencyFilter);
      if (sortBy) params.append('sort_by', sortBy);
      
      const response = await axios.get(`/api/reports/loyalty/customers/?${params}`);
      setCustomerList(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load customer list');
    } finally {
      setLoading(false);
    }
  };

  const fetchRepeatData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/reports/loyalty/repeat/');
      setRepeatData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load repeat customer data');
    } finally {
      setLoading(false);
    }
  };

  const fetchFrequencyData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/reports/loyalty/frequency/');
      setFrequencyData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load frequency data');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecencyData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/reports/loyalty/recency/');
      setRecencyData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load recency data');
    } finally {
      setLoading(false);
    }
  };

  const fetchLtvData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/reports/loyalty/ltv/');
      setLtvData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load LTV data');
    } finally {
      setLoading(false);
    }
  };

  const fetchCohortData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/reports/loyalty/cohorts/');
      setCohortData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load cohort data');
    } finally {
      setLoading(false);
    }
  };

  const getLoyaltyBadge = (segment) => {
    const badges = {
      'prospect': { label: 'Prospect', class: 'badge-gray' },
      'new': { label: 'New', class: 'badge-blue' },
      'repeat': { label: 'Repeat', class: 'badge-yellow' },
      'loyal': { label: 'Loyal', class: 'badge-green' },
    };
    const badge = badges[segment] || badges['prospect'];
    return <span className={`loyalty-badge ${badge.class}`}>{badge.label}</span>;
  };

  const getRecencyBadge = (status) => {
    const badges = {
      'active': { label: 'Active', class: 'badge-green' },
      'at_risk': { label: 'At Risk', class: 'badge-yellow' },
      'inactive': { label: 'Inactive', class: 'badge-red' },
      'never_ordered': { label: 'Never Ordered', class: 'badge-gray' },
    };
    const badge = badges[status] || badges['never_ordered'];
    return <span className={`recency-badge ${badge.class}`}>{badge.label}</span>;
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const renderDashboard = () => {
    if (!dashboardData) return null;
    const { summary, segment_counts, recency_counts, top_by_revenue, at_risk_customers } = dashboardData;

    return (
      <div className="analytics-dashboard">
        {/* Summary KPIs */}
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-icon">👥</div>
            <div className="kpi-content">
              <div className="kpi-value">{summary.customers_with_orders}</div>
              <div className="kpi-label">Active Customers</div>
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-icon">💰</div>
            <div className="kpi-content">
              <div className="kpi-value">{formatCurrency(summary.total_revenue)}</div>
              <div className="kpi-label">Total Revenue</div>
            </div>
          </div>
          <div className="kpi-card">
            <div className="kpi-icon">📊</div>
            <div className="kpi-content">
              <div className="kpi-value">{formatCurrency(summary.avg_lifetime_value)}</div>
              <div className="kpi-label">Avg. Lifetime Value</div>
            </div>
          </div>
          <div className="kpi-card highlight">
            <div className="kpi-icon">🔄</div>
            <div className="kpi-content">
              <div className="kpi-value">{summary.repeat_rate_percent}%</div>
              <div className="kpi-label">Repeat Rate</div>
            </div>
          </div>
        </div>

        {/* Segment Charts */}
        <div className="charts-row">
          <div className="chart-card">
            <h3>Loyalty Segments</h3>
            <div className="segment-bars">
              {Object.entries(segment_counts).map(([segment, count]) => (
                <div key={segment} className="segment-bar-row">
                  <span className="segment-label">{getLoyaltyBadge(segment)}</span>
                  <div className="segment-bar-container">
                    <div 
                      className={`segment-bar segment-${segment}`}
                      style={{ width: `${(count / summary.total_customers) * 100}%` }}
                    ></div>
                  </div>
                  <span className="segment-count">{count}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="chart-card">
            <h3>Recency Status</h3>
            <div className="segment-bars">
              {Object.entries(recency_counts).filter(([s]) => s !== 'never_ordered').map(([status, count]) => (
                <div key={status} className="segment-bar-row">
                  <span className="segment-label">{getRecencyBadge(status)}</span>
                  <div className="segment-bar-container">
                    <div 
                      className={`segment-bar recency-${status}`}
                      style={{ width: `${(count / summary.customers_with_orders) * 100}%` }}
                    ></div>
                  </div>
                  <span className="segment-count">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Customers & At Risk */}
        <div className="tables-row">
          <div className="table-card">
            <h3>🏆 Top Customers by Revenue</h3>
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Orders</th>
                  <th>Revenue</th>
                  <th>Segment</th>
                </tr>
              </thead>
              <tbody>
                {top_by_revenue.map(c => (
                  <tr key={c.customer_id}>
                    <td>
                      <Link to={`/customers/${c.customer_id}`}>{c.customer_name}</Link>
                    </td>
                    <td>{c.total_orders}</td>
                    <td>{formatCurrency(c.total_revenue)}</td>
                    <td>{getLoyaltyBadge(c.loyalty_segment)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="table-card warning">
            <h3>⚠️ At-Risk Customers</h3>
            <p className="card-subtitle">Haven't ordered in 31-90 days</p>
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Last Order</th>
                  <th>Revenue</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {at_risk_customers.length === 0 ? (
                  <tr><td colSpan="4" className="no-data">No at-risk customers!</td></tr>
                ) : (
                  at_risk_customers.map(c => (
                    <tr key={c.customer_id}>
                      <td>
                        <Link to={`/customers/${c.customer_id}`}>{c.customer_name}</Link>
                      </td>
                      <td>{c.recency_days} days ago</td>
                      <td>{formatCurrency(c.total_revenue)}</td>
                      <td>
                        <a href={`tel:${c.mobile}`} className="action-link">📞 Call</a>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Insights */}
        <div className="insights-section">
          <h3>💡 Engagement Tips</h3>
          <div className="insights-grid">
            <div className="insight-card">
              <h4>Convert New to Repeat</h4>
              <p>You have <strong>{segment_counts.new}</strong> new customers. Send them a special offer for their second order within 7 days!</p>
            </div>
            <div className="insight-card">
              <h4>Reward Loyal Customers</h4>
              <p><strong>{segment_counts.loyal}</strong> loyal customers drive most of your revenue. Consider a loyalty discount or early access to new items.</p>
            </div>
            <div className="insight-card">
              <h4>Win Back At-Risk</h4>
              <p><strong>{recency_counts.at_risk}</strong> customers haven't ordered in 31-90 days. A "We miss you" message with 10% off can bring them back!</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderCustomerList = () => {
    if (!customerList) return null;

    return (
      <div className="customer-list-section">
        <div className="filters-row">
          <div className="filter-group">
            <label>Loyalty Segment:</label>
            <select value={loyaltyFilter} onChange={(e) => setLoyaltyFilter(e.target.value)}>
              <option value="">All</option>
              <option value="prospect">Prospect</option>
              <option value="new">New (1 order)</option>
              <option value="repeat">Repeat (2-4 orders)</option>
              <option value="loyal">Loyal (5+ orders)</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Recency Status:</label>
            <select value={recencyFilter} onChange={(e) => setRecencyFilter(e.target.value)}>
              <option value="">All</option>
              <option value="active">Active (&lt;30 days)</option>
              <option value="at_risk">At Risk (31-90 days)</option>
              <option value="inactive">Inactive (&gt;90 days)</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Sort By:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="total_revenue">Total Revenue</option>
              <option value="total_orders">Total Orders</option>
              <option value="avg_order_value">Avg Order Value</option>
              <option value="recency_days">Most Recent</option>
            </select>
          </div>
        </div>

        <div className="results-count">{customerList.count} customers found</div>

        <table className="analytics-table full-width">
          <thead>
            <tr>
              <th>Customer</th>
              <th>Contact</th>
              <th>Orders</th>
              <th>Revenue</th>
              <th>Avg Order</th>
              <th>Last Order</th>
              <th>Loyalty</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {customerList.data.map(c => (
              <tr key={c.customer_id}>
                <td>
                  <Link to={`/customers/${c.customer_id}`}>{c.customer_name}</Link>
                  {c.apartment && <div className="sub-text">{c.apartment}</div>}
                </td>
                <td>{c.mobile}</td>
                <td>{c.total_orders}</td>
                <td>{formatCurrency(c.total_revenue)}</td>
                <td>{formatCurrency(c.avg_order_value)}</td>
                <td>
                  {c.last_order_date ? (
                    <>
                      {c.last_order_date}
                      <div className="sub-text">{c.recency_days} days ago</div>
                    </>
                  ) : '-'}
                </td>
                <td>{getLoyaltyBadge(c.loyalty_segment)}</td>
                <td>{getRecencyBadge(c.recency_status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderRepeatReport = () => {
    if (!repeatData) return null;
    const { summary, one_time_customers, repeat_customers } = repeatData;

    return (
      <div className="repeat-report">
        <div className="summary-cards">
          <div className="summary-card">
            <div className="summary-value">{summary.repeat_rate_percent}%</div>
            <div className="summary-label">Repeat Rate</div>
          </div>
          <div className="summary-card">
            <div className="summary-value">{summary.one_time_count}</div>
            <div className="summary-label">One-Time Customers</div>
          </div>
          <div className="summary-card">
            <div className="summary-value">{summary.repeat_count}</div>
            <div className="summary-label">Repeat Customers</div>
          </div>
          <div className="summary-card highlight">
            <div className="summary-value">{summary.repeat_revenue_percent}%</div>
            <div className="summary-label">Revenue from Repeat</div>
          </div>
        </div>

        <div className="comparison-chart">
          <h3>Revenue Comparison</h3>
          <div className="bar-comparison">
            <div className="comparison-bar one-time" style={{ flex: summary.one_time_revenue }}>
              <span>One-Time: {formatCurrency(summary.one_time_revenue)}</span>
            </div>
            <div className="comparison-bar repeat" style={{ flex: summary.repeat_revenue }}>
              <span>Repeat: {formatCurrency(summary.repeat_revenue)}</span>
            </div>
          </div>
        </div>

        <div className="tables-row">
          <div className="table-card">
            <h3>One-Time Customers (Potential Converts)</h3>
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Revenue</th>
                  <th>Last Order</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {one_time_customers.map(c => (
                  <tr key={c.customer_id}>
                    <td><Link to={`/customers/${c.customer_id}`}>{c.customer_name}</Link></td>
                    <td>{formatCurrency(c.total_revenue)}</td>
                    <td>{c.recency_days} days ago</td>
                    <td>{getRecencyBadge(c.recency_status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="table-card">
            <h3>Top Repeat Customers</h3>
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Orders</th>
                  <th>Revenue</th>
                  <th>Frequency</th>
                </tr>
              </thead>
              <tbody>
                {repeat_customers.map(c => (
                  <tr key={c.customer_id}>
                    <td><Link to={`/customers/${c.customer_id}`}>{c.customer_name}</Link></td>
                    <td>{c.total_orders}</td>
                    <td>{formatCurrency(c.total_revenue)}</td>
                    <td>{c.order_frequency}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  const renderFrequencyReport = () => {
    if (!frequencyData) return null;
    const { frequency_summary, weekly_customers, biweekly_customers, monthly_customers } = frequencyData;

    return (
      <div className="frequency-report">
        <div className="frequency-summary">
          <h3>Purchase Frequency Distribution</h3>
          <div className="frequency-bars">
            {Object.entries(frequency_summary).map(([freq, data]) => (
              <div key={freq} className="frequency-row">
                <span className="freq-label">{freq.replace('_', ' ')}</span>
                <div className="freq-bar-container">
                  <div 
                    className={`freq-bar freq-${freq}`}
                    style={{ width: `${Math.min((data.count / 10) * 100, 100)}%` }}
                  >
                    <span className="freq-count">{data.count} customers</span>
                  </div>
                </div>
                <span className="freq-revenue">{formatCurrency(data.total_revenue)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="frequency-tables">
          {weekly_customers.length > 0 && (
            <div className="table-card">
              <h3>🏃 Weekly Orderers</h3>
              <table className="analytics-table">
                <thead>
                  <tr><th>Customer</th><th>Orders</th><th>Revenue</th><th>Avg Days</th></tr>
                </thead>
                <tbody>
                  {weekly_customers.map(c => (
                    <tr key={c.customer_id}>
                      <td><Link to={`/customers/${c.customer_id}`}>{c.customer_name}</Link></td>
                      <td>{c.total_orders}</td>
                      <td>{formatCurrency(c.total_revenue)}</td>
                      <td>{c.avg_days_between_orders} days</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {monthly_customers.length > 0 && (
            <div className="table-card">
              <h3>📅 Monthly Orderers</h3>
              <table className="analytics-table">
                <thead>
                  <tr><th>Customer</th><th>Orders</th><th>Revenue</th><th>Avg Days</th></tr>
                </thead>
                <tbody>
                  {monthly_customers.map(c => (
                    <tr key={c.customer_id}>
                      <td><Link to={`/customers/${c.customer_id}`}>{c.customer_name}</Link></td>
                      <td>{c.total_orders}</td>
                      <td>{formatCurrency(c.total_revenue)}</td>
                      <td>{c.avg_days_between_orders} days</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderRecencyReport = () => {
    if (!recencyData) return null;
    const { recency_summary, insights, active_customers, at_risk_customers, inactive_customers } = recencyData;

    return (
      <div className="recency-report">
        <div className="summary-cards">
          <div className="summary-card green">
            <div className="summary-value">{recency_summary.active?.count || 0}</div>
            <div className="summary-label">Active (&lt;30 days)</div>
            <div className="summary-sub">{formatCurrency(recency_summary.active?.total_revenue || 0)}</div>
          </div>
          <div className="summary-card yellow">
            <div className="summary-value">{recency_summary.at_risk?.count || 0}</div>
            <div className="summary-label">At Risk (31-90 days)</div>
            <div className="summary-sub">{formatCurrency(recency_summary.at_risk?.total_revenue || 0)}</div>
          </div>
          <div className="summary-card red">
            <div className="summary-value">{recency_summary.inactive?.count || 0}</div>
            <div className="summary-label">Inactive (&gt;90 days)</div>
            <div className="summary-sub">{formatCurrency(recency_summary.inactive?.total_revenue || 0)}</div>
          </div>
        </div>

        {insights.length > 0 && (
          <div className="insights-section">
            <h3>🎯 Action Items</h3>
            {insights.map((insight, idx) => (
              <div key={idx} className={`insight-alert ${insight.type}`}>
                <h4>{insight.title}</h4>
                <p>{insight.message}</p>
                {insight.customers && (
                  <div className="insight-customers">
                    {insight.customers.map(c => (
                      <Link key={c.customer_id} to={`/customers/${c.customer_id}`} className="customer-chip">
                        {c.customer_name} ({formatCurrency(c.total_revenue)})
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="recency-tables">
          <div className="table-card">
            <h3>✅ Active Customers</h3>
            <table className="analytics-table">
              <thead>
                <tr><th>Customer</th><th>Last Order</th><th>Orders</th><th>Revenue</th></tr>
              </thead>
              <tbody>
                {active_customers.map(c => (
                  <tr key={c.customer_id}>
                    <td><Link to={`/customers/${c.customer_id}`}>{c.customer_name}</Link></td>
                    <td>{c.recency_days} days ago</td>
                    <td>{c.total_orders}</td>
                    <td>{formatCurrency(c.total_revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="table-card warning">
            <h3>⚠️ At Risk - Need Attention</h3>
            <table className="analytics-table">
              <thead>
                <tr><th>Customer</th><th>Last Order</th><th>Revenue</th><th>Action</th></tr>
              </thead>
              <tbody>
                {at_risk_customers.map(c => (
                  <tr key={c.customer_id}>
                    <td><Link to={`/customers/${c.customer_id}`}>{c.customer_name}</Link></td>
                    <td>{c.recency_days} days ago</td>
                    <td>{formatCurrency(c.total_revenue)}</td>
                    <td><a href={`tel:${c.mobile}`}>📞 Call</a></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  const renderLtvReport = () => {
    if (!ltvData) return null;
    const { summary, ltv_distribution, top_customers } = ltvData;

    return (
      <div className="ltv-report">
        <div className="summary-cards">
          <div className="summary-card">
            <div className="summary-value">{formatCurrency(summary.total_ltv)}</div>
            <div className="summary-label">Total Customer LTV</div>
          </div>
          <div className="summary-card">
            <div className="summary-value">{formatCurrency(summary.avg_ltv)}</div>
            <div className="summary-label">Average LTV</div>
          </div>
          <div className="summary-card">
            <div className="summary-value">{formatCurrency(summary.median_ltv)}</div>
            <div className="summary-label">Median LTV</div>
          </div>
          <div className="summary-card highlight">
            <div className="summary-value">{summary.top_20_revenue_percent}%</div>
            <div className="summary-label">Revenue from Top 20%</div>
          </div>
        </div>

        <div className="ltv-distribution">
          <h3>LTV Distribution</h3>
          <div className="distribution-bars">
            {Object.entries(ltv_distribution).map(([bucket, data]) => (
              <div key={bucket} className="distribution-row">
                <span className="bucket-label">₹{bucket}</span>
                <div className="bucket-bar-container">
                  <div 
                    className="bucket-bar"
                    style={{ width: `${(data.count / summary.total_customers) * 100}%` }}
                  >
                    {data.count}
                  </div>
                </div>
                <span className="bucket-revenue">{formatCurrency(data.total_revenue)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="table-card">
          <h3>🏆 Top 20 Customers by Lifetime Value</h3>
          <table className="analytics-table full-width">
            <thead>
              <tr>
                <th>#</th>
                <th>Customer</th>
                <th>Orders</th>
                <th>LTV</th>
                <th>Avg Order</th>
                <th>First Order</th>
                <th>Segment</th>
              </tr>
            </thead>
            <tbody>
              {top_customers.map((c, idx) => (
                <tr key={c.customer_id}>
                  <td>{idx + 1}</td>
                  <td><Link to={`/customers/${c.customer_id}`}>{c.customer_name}</Link></td>
                  <td>{c.total_orders}</td>
                  <td className="highlight-value">{formatCurrency(c.total_revenue)}</td>
                  <td>{formatCurrency(c.avg_order_value)}</td>
                  <td>{c.first_order_date}</td>
                  <td>{getLoyaltyBadge(c.loyalty_segment)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderCohortReport = () => {
    if (!cohortData) return null;
    const { cohorts } = cohortData;

    return (
      <div className="cohort-report">
        <h3>Monthly Cohort Retention</h3>
        <p className="report-description">
          Tracks how many customers from each monthly cohort continue to order in subsequent months.
        </p>

        <table className="cohort-table">
          <thead>
            <tr>
              <th>Cohort</th>
              <th>Size</th>
              <th>M0 (First Month)</th>
              <th>M1</th>
              <th>M2</th>
              <th>M3</th>
            </tr>
          </thead>
          <tbody>
            {cohorts.map(cohort => (
              <tr key={cohort.cohort}>
                <td className="cohort-month">{cohort.cohort}</td>
                <td>{cohort.size}</td>
                {['M0', 'M1', 'M2', 'M3'].map(month => {
                  const data = cohort.months[month];
                  if (!data) return <td key={month} className="no-data">-</td>;
                  const intensity = Math.min(data.retention_percent / 100, 1);
                  return (
                    <td 
                      key={month} 
                      className="retention-cell"
                      style={{ 
                        backgroundColor: `rgba(46, 125, 50, ${intensity})`,
                        color: intensity > 0.5 ? 'white' : 'black'
                      }}
                    >
                      {data.retention_percent}%
                      <div className="retention-count">({data.active})</div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>

        <div className="cohort-insight">
          <h4>📈 Reading the Cohort Table</h4>
          <p>
            <strong>M0</strong> = First month (always 100% for active cohort). 
            <strong>M1, M2, M3</strong> = Retention in subsequent months.
            Higher percentages in later months indicate better customer retention.
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="customer-analytics-page">
      <div className="page-header">
        <div className="header-content">
          <h1>👥 Customer Analytics</h1>
          <p className="page-subtitle">Loyalty insights and engagement opportunities</p>
        </div>
      </div>

      <div className="analytics-tabs">
        <button 
          className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={`tab-btn ${activeTab === 'customers' ? 'active' : ''}`}
          onClick={() => setActiveTab('customers')}
        >
          👥 All Customers
        </button>
        <button 
          className={`tab-btn ${activeTab === 'repeat' ? 'active' : ''}`}
          onClick={() => setActiveTab('repeat')}
        >
          🔄 Repeat Analysis
        </button>
        <button 
          className={`tab-btn ${activeTab === 'frequency' ? 'active' : ''}`}
          onClick={() => setActiveTab('frequency')}
        >
          📅 Frequency
        </button>
        <button 
          className={`tab-btn ${activeTab === 'recency' ? 'active' : ''}`}
          onClick={() => setActiveTab('recency')}
        >
          ⏰ Recency
        </button>
        <button 
          className={`tab-btn ${activeTab === 'ltv' ? 'active' : ''}`}
          onClick={() => setActiveTab('ltv')}
        >
          💎 Lifetime Value
        </button>
        <button 
          className={`tab-btn ${activeTab === 'cohorts' ? 'active' : ''}`}
          onClick={() => setActiveTab('cohorts')}
        >
          📈 Cohorts
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading analytics...</div>
      ) : (
        <div className="tab-content">
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'customers' && renderCustomerList()}
          {activeTab === 'repeat' && renderRepeatReport()}
          {activeTab === 'frequency' && renderFrequencyReport()}
          {activeTab === 'recency' && renderRecencyReport()}
          {activeTab === 'ltv' && renderLtvReport()}
          {activeTab === 'cohorts' && renderCohortReport()}
        </div>
      )}
    </div>
  );
}

export default CustomerAnalytics;

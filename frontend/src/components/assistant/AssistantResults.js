import React from 'react';
import { Link } from 'react-router-dom';
import { exportResultCsv } from '../../utils/exportCsv';
import './AssistantResults.css';

const formatCurrency = (n) => `₹${parseFloat(n || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

const ExportButton = ({ type, data }) => {
  if (!data) return null;
  return (
    <button
      type="button"
      className="export-csv-btn"
      onClick={() => exportResultCsv(type, data)}
      title="Download as CSV"
    >
      ↓ CSV
    </button>
  );
};

export const OrdersResult = ({ data }) => {
  if (!data?.orders?.length) return null;

  return (
    <div className="assistant-result assistant-orders">
      <div className="result-toolbar">
        <div className="result-summary">
          <span>{data.count} order(s)</span>
          <span>{formatCurrency(data.total_revenue)} revenue</span>
          <span className="profit">{formatCurrency(data.total_profit)} profit</span>
        </div>
        <ExportButton type="orders" data={data} />
      </div>
      <div className="result-table-wrap">
        <table className="result-table">
          <thead>
            <tr>
              <th>Order</th>
              <th>Customer</th>
              <th>Date</th>
              <th>Status</th>
              <th>Payment</th>
              <th>Revenue</th>
              <th>Profit</th>
              <th>Items</th>
            </tr>
          </thead>
          <tbody>
            {data.orders.map((order) => (
              <tr key={order.id}>
                <td>
                  <Link to={`/orders/${order.id}`} className="result-link">
                    {order.order_number}
                  </Link>
                </td>
                <td>
                  <div className="cell-main">{order.customer?.name}</div>
                  <div className="cell-sub">{order.customer?.mobile}</div>
                </td>
                <td>{new Date(order.order_date).toLocaleDateString('en-IN')}</td>
                <td><span className={`pill status-${order.status}`}>{order.status}</span></td>
                <td><span className={`pill pay-${order.payment_status}`}>{order.payment_status}</span></td>
                <td className="num">{formatCurrency(order.total_revenue)}</td>
                <td className="num profit">{formatCurrency(order.total_profit)}</td>
                <td className="items-cell">
                  {order.matching_items?.map((item, i) => (
                    <div key={i} className="item-line">
                      {item.product_name} {item.product_unit} ×{item.quantity}
                    </div>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const CustomersResult = ({ data }) => {
  if (!data?.customers?.length) return null;

  const sortByRevenue = data.sort_by === 'revenue';
  const multi = data.customers.length > 1;

  return (
    <div className="assistant-result assistant-customers">
      <div className="result-toolbar">
        <div className="result-period">
          {data.start_date} → {data.end_date}
          <span className="muted"> sorted by {data.sort_by}</span>
        </div>
        <ExportButton type="customers" data={data} />
      </div>

      {multi && (
        <div className="result-table-wrap">
          <table className="result-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Customer</th>
                <th>Mobile</th>
                <th>Orders</th>
                <th className={sortByRevenue ? 'highlight-col' : ''}>Revenue</th>
                <th className={!sortByRevenue ? 'highlight-col' : ''}>Profit</th>
              </tr>
            </thead>
            <tbody>
              {data.customers.map((customer, index) => (
                <tr key={customer.customer_id}>
                  <td>{index + 1}</td>
                  <td>
                    <Link to={`/customers/${customer.customer_id}`} className="result-link">
                      {customer.customer_name}
                    </Link>
                  </td>
                  <td className="cell-sub">{customer.mobile}</td>
                  <td className="num">{customer.order_count}</td>
                  <td className={`num ${sortByRevenue ? 'highlight-val' : ''}`}>
                    {formatCurrency(customer.total_spent)}
                  </td>
                  <td className={`num profit ${!sortByRevenue ? 'highlight-val' : ''}`}>
                    {formatCurrency(customer.total_profit)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {(!multi || data.customers.length <= 5) &&
        data.customers.map((customer) => (
        <div key={`detail-${customer.customer_id}`} className="customer-card">
          {!multi && (
            <div className="customer-card-header">
              <div>
                <h4>
                  <Link to={`/customers/${customer.customer_id}`} className="result-link">
                    {customer.customer_name}
                  </Link>
                </h4>
                <p className="cell-sub">
                  {customer.mobile}
                  {customer.apartment_name && ` · ${customer.apartment_name}`}
                  {customer.block && ` · ${customer.block}`}
                </p>
              </div>
              <div className="customer-metrics">
                <div><strong>{formatCurrency(customer.total_profit)}</strong> profit</div>
                <div>{formatCurrency(customer.total_spent)} revenue</div>
                <div>{customer.order_count} orders</div>
              </div>
            </div>
          )}
          {customer.orders?.length > 0 && (!multi || data.customers.length <= 5) && (
            <div className="customer-orders">
              {multi && (
                <div className="customer-orders-title">{customer.customer_name} — purchases</div>
              )}
              {!multi && (
                <div className="customer-orders-title">Individual purchases</div>
              )}
              <table className="result-table compact">
                <thead>
                  <tr>
                    <th>Order</th>
                    <th>Date</th>
                    <th>Items</th>
                    <th>Spent</th>
                    <th>Profit</th>
                  </tr>
                </thead>
                <tbody>
                  {customer.orders.map((order) => (
                    <tr key={order.order_number}>
                      <td>{order.order_number}</td>
                      <td>{new Date(order.order_date).toLocaleDateString('en-IN')}</td>
                      <td className="items-cell">
                        {order.items?.map((item, i) => (
                          <div key={i} className="item-line">
                            {item.product_name} {item.product_unit} ×{item.quantity}
                          </div>
                        ))}
                      </td>
                      <td className="num">{formatCurrency(order.total_spent)}</td>
                      <td className="num profit">{formatCurrency(order.total_profit)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export const ProductsResult = ({ data }) => {
  if (!data?.products?.length) return null;

  return (
    <div className="assistant-result assistant-products">
      <div className="result-toolbar">
        <span className="muted">{data.count} product(s)</span>
        <ExportButton type="products" data={data} />
      </div>
      <div className="result-table-wrap">
        <table className="result-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Unit</th>
              <th>Category</th>
              <th>Price</th>
              <th>Margin</th>
            </tr>
          </thead>
          <tbody>
            {data.products.map((p) => (
              <tr key={p.id}>
                <td>
                  <Link to={`/catalog/${p.id}`} className="result-link">{p.name}</Link>
                </td>
                <td>{p.unit}</td>
                <td>{p.category}</td>
                <td className="num">{formatCurrency(p.selling_price)}</td>
                <td className="num">{parseFloat(p.margin_percent || 0).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const OfferingsResult = ({ data }) => {
  if (!data?.offerings?.length) return null;

  return (
    <div className="assistant-result assistant-offerings">
      <div className="result-toolbar">
        <span className="muted">{data.count} offering(s)</span>
        <ExportButton type="offerings" data={data} />
      </div>
      {data.offerings.map((offering) => (
        <div key={offering.id} className="offering-card">
          <div className="offering-card-header">
            <h4>{new Date(offering.offering_date).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })}</h4>
            <span className={`pill ${offering.is_active ? 'status-confirmed' : 'status-cancelled'}`}>
              {offering.status}
            </span>
          </div>
          {offering.notes && <p className="cell-sub offering-notes">{offering.notes}</p>}
          <div className="result-table-wrap">
            <table className="result-table compact">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Unit</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Qty</th>
                </tr>
              </thead>
              <tbody>
                {(offering.items || []).map((item, i) => (
                  <tr key={i}>
                    <td>{item.product_name}</td>
                    <td>{item.product_unit}</td>
                    <td>{item.category}</td>
                    <td className="num">{formatCurrency(item.selling_price)}</td>
                    <td className="num">{item.available_quantity ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
};

export const PaymentTrendsResult = ({ data }) => {
  if (!data?.by_method) return null;
  const total = parseFloat(data.total_amount || 0);

  return (
    <div className="assistant-result assistant-payments">
      <div className="result-toolbar">
        <div className="result-summary">
          <span>{data.total_count} payment(s)</span>
          <span>{formatCurrency(total)} collected</span>
          <span className="muted">{data.start_date} → {data.end_date}</span>
        </div>
        <ExportButton type="payment_trends" data={data} />
      </div>
      <div className="payment-method-grid">
        {Object.entries(data.by_method).map(([method, stats]) => {
          const amount = parseFloat(stats.amount || 0);
          const pct = total ? Math.round((amount / total) * 100) : 0;
          return (
            <div key={method} className="payment-method-card">
              <div className="method-label">{stats.label || method}</div>
              <div className="method-amount">{formatCurrency(amount)}</div>
              <div className="method-meta">{stats.count} payment(s) · {pct}%</div>
              <div className="method-bar">
                <div className="method-bar-fill" style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const renderAssistantData = (type, data) => {
  if (!data) return null;
  switch (type) {
    case 'orders':
      return <OrdersResult data={data} />;
    case 'customers':
      return <CustomersResult data={data} />;
    case 'products':
      return <ProductsResult data={data} />;
    case 'offerings':
      return <OfferingsResult data={data} />;
    case 'payment_trends':
      return <PaymentTrendsResult data={data} />;
    default:
      return null;
  }
};

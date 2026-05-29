/** Build and download a CSV file in the browser. */
export const downloadCsv = (filename, headers, rows) => {
  const escape = (value) => {
    const text = value == null ? '' : String(value);
    if (/[",\n]/.test(text)) {
      return `"${text.replace(/"/g, '""')}"`;
    }
    return text;
  };

  const lines = [
    headers.map(escape).join(','),
    ...rows.map((row) => row.map(escape).join(',')),
  ];
  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
};

export const exportOrdersCsv = (data) => {
  if (!data?.orders?.length) return;
  downloadCsv(
    'orders.csv',
    ['Order', 'Customer', 'Mobile', 'Date', 'Status', 'Payment', 'Revenue', 'Profit', 'Items'],
    data.orders.map((order) => [
      order.order_number,
      order.customer?.name,
      order.customer?.mobile,
      order.order_date,
      order.status,
      order.payment_status,
      order.total_revenue,
      order.total_profit,
      (order.matching_items || [])
        .map((i) => `${i.product_name} ${i.product_unit} x${i.quantity}`)
        .join('; '),
    ]),
  );
};

export const exportCustomersCsv = (data) => {
  if (!data?.customers?.length) return;
  downloadCsv(
    'customers.csv',
    ['Rank', 'Customer', 'Mobile', 'Orders', 'Revenue', 'Profit'],
    data.customers.map((c, i) => [
      i + 1,
      c.customer_name,
      c.mobile,
      c.order_count,
      c.total_spent,
      c.total_profit,
    ]),
  );
};

export const exportProductsCsv = (data) => {
  if (!data?.products?.length) return;
  downloadCsv(
    'products.csv',
    ['Product', 'Unit', 'Category', 'Price', 'Margin %'],
    data.products.map((p) => [p.name, p.unit, p.category, p.selling_price, p.margin_percent]),
  );
};

export const exportOfferingsCsv = (data) => {
  if (!data?.offerings?.length) return;
  const rows = [];
  data.offerings.forEach((offering) => {
    (offering.items || []).forEach((item) => {
      rows.push([
        offering.offering_date,
        offering.status,
        item.product_name,
        item.product_unit,
        item.category,
        item.selling_price,
        item.available_quantity ?? '',
      ]);
    });
  });
  downloadCsv(
    'daily-offerings.csv',
    ['Date', 'Status', 'Product', 'Unit', 'Category', 'Price', 'Available Qty'],
    rows,
  );
};

export const exportPaymentTrendsCsv = (data) => {
  if (!data?.by_method) return;
  const total = parseFloat(data.total_amount || 0);
  downloadCsv(
    'payment-trends.csv',
    ['Method', 'Count', 'Amount', 'Share %'],
    Object.entries(data.by_method).map(([method, stats]) => {
      const amount = parseFloat(stats.amount || 0);
      const share = total ? ((amount / total) * 100).toFixed(1) : '0';
      return [stats.label || method, stats.count, amount, share];
    }),
  );
};

export const exportResultCsv = (type, data) => {
  switch (type) {
    case 'orders':
      exportOrdersCsv(data);
      break;
    case 'customers':
      exportCustomersCsv(data);
      break;
    case 'products':
      exportProductsCsv(data);
      break;
    case 'offerings':
      exportOfferingsCsv(data);
      break;
    case 'payment_trends':
      exportPaymentTrendsCsv(data);
      break;
    default:
      break;
  }
};

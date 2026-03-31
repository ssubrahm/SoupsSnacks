/**
 * Utility functions for formatting numbers and currency
 */

/**
 * Format currency with Indian Rupee symbol
 * Uses compact notation for large numbers
 */
export const formatCurrency = (amount, compact = false) => {
  if (amount === null || amount === undefined) return '₹0.00';
  
  const num = parseFloat(amount);
  
  if (compact && num >= 100000) {
    // 1 Lakh and above -> 1.5L
    const lakhs = num / 100000;
    return `₹${lakhs.toFixed(1)}L`;
  } else if (compact && num >= 1000) {
    // 1000 and above -> 1.5K
    const thousands = num / 1000;
    return `₹${thousands.toFixed(1)}K`;
  }
  
  return `₹${num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

/**
 * Format number with compact notation
 */
export const formatNumber = (num, compact = false) => {
  if (num === null || num === undefined) return '0';
  
  const number = parseFloat(num);
  
  if (compact && number >= 100000) {
    const lakhs = number / 100000;
    return `${lakhs.toFixed(1)}L`;
  } else if (compact && number >= 1000) {
    const thousands = number / 1000;
    return `${thousands.toFixed(1)}K`;
  }
  
  return number.toLocaleString('en-IN');
};

/**
 * Format percentage
 */
export const formatPercent = (value, decimals = 1) => {
  if (value === null || value === undefined) return '0%';
  return `${parseFloat(value).toFixed(decimals)}%`;
};

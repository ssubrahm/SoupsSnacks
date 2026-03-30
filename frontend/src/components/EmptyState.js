import React from 'react';
import { Link } from 'react-router-dom';

const EmptyState = ({ 
  icon = '📭', 
  title = 'No data found', 
  message = '', 
  actionText = '', 
  actionLink = '',
  onAction = null 
}) => {
  return (
    <div style={{
      textAlign: 'center',
      padding: '4rem 2rem',
      background: 'var(--bg-secondary)',
      borderRadius: '12px',
      border: '2px dashed var(--border-color)'
    }}>
      <div style={{ fontSize: '4rem', marginBottom: '1rem', opacity: 0.4 }}>
        {icon}
      </div>
      <h3 style={{ 
        color: 'var(--text-primary)', 
        marginBottom: '0.5rem',
        fontSize: '1.25rem'
      }}>
        {title}
      </h3>
      {message && (
        <p style={{ 
          color: 'var(--text-secondary)', 
          marginBottom: actionText ? '1.5rem' : 0,
          maxWidth: '400px',
          marginLeft: 'auto',
          marginRight: 'auto'
        }}>
          {message}
        </p>
      )}
      {actionText && actionLink && (
        <Link to={actionLink} className="btn-primary">
          {actionText}
        </Link>
      )}
      {actionText && onAction && !actionLink && (
        <button onClick={onAction} className="btn-primary">
          {actionText}
        </button>
      )}
    </div>
  );
};

export default EmptyState;

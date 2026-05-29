import React from 'react';

const Loading = ({ message = 'Loading...', fullPage = false }) => {
  const style = fullPage ? {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '60vh',
    color: 'var(--text-secondary)'
  } : {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '3rem 2rem',
    color: 'var(--text-secondary)'
  };

  return (
    <div style={style}>
      <div className="loading-spinner" style={{
        width: '40px',
        height: '40px',
        border: '3px solid var(--border-color)',
        borderTopColor: 'var(--primary-color)',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
        marginBottom: '1rem'
      }} />
      <span style={{ fontSize: '0.9375rem' }}>{message}</span>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default Loading;

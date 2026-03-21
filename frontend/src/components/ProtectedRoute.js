import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        color: 'var(--text-secondary)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⏳</div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole) {
    const hasAccess = requiredRole === 'admin' ? user.role === 'admin' :
                      requiredRole === 'operator' ? ['admin', 'operator'].includes(user.role) :
                      requiredRole === 'cook' ? ['admin', 'cook'].includes(user.role) :
                      true;
    
    if (!hasAccess) {
      return (
        <div style={{
          padding: '2rem',
          textAlign: 'center',
          color: 'var(--text-secondary)'
        }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🚫</div>
          <h2 style={{ color: 'var(--text-primary)' }}>Access Denied</h2>
          <p>You don't have permission to access this page.</p>
          <p>Your role: <strong>{user.role}</strong></p>
        </div>
      );
    }
  }

  return children;
};

export default ProtectedRoute;

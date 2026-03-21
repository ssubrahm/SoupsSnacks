import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import Logo from '../components/Logo';
import './Login.css';

const Login = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.post('/accounts/login/', {
        username,
        password
      });
      
      if (response.data.user) {
        login(response.data.user);
        navigate('/');
      }
    } catch (err) {
      console.error('Login error:', err);
      if (err.response?.data) {
        const errorData = err.response.data;
        if (typeof errorData === 'object') {
          setError(Object.values(errorData).flat().join(' '));
        } else {
          setError('Invalid username or password');
        }
      } else {
        setError('Cannot connect to server. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <Logo size={80} />
          <h1>Soups, Snacks & More</h1>
          <p className="login-subtitle">Order Management System</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <h2>Sign In</h2>
          
          {error && (
            <div className="login-error">
              ✗ {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              autoFocus
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>

          <div className="test-credentials">
            <p><strong>Test Credentials:</strong></p>
            <p>Admin: <code>admin / admin123</code></p>
            <p>Operator: <code>operator / operator123</code></p>
            <p>Cook: <code>cook / cook123</code></p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;

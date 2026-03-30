import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Logo from './Logo';
import './Layout.css';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth > 768);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= 768;
      setIsMobile(mobile);
      if (!mobile && !sidebarOpen) {
        setSidebarOpen(true);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [sidebarOpen]);

  // Close sidebar on mobile when route changes
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  }, [location.pathname, isMobile]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <header className="header">
        <button 
          className="menu-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle menu"
        >
          ☰
        </button>
        <div className="header-brand">
          <Logo size={45} />
          <div className="header-text">
            <h1>Soups, Snacks & More</h1>
            <span className="header-subtitle">Order Management System</span>
          </div>
        </div>
        <div className="header-actions">
          {user && (
            <div className="user-info">
              <span className="user-name">{user.first_name || user.username}</span>
              <span className="user-role">{user.role}</span>
            </div>
          )}
          <button 
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
          {user && (
            <button 
              className="logout-button"
              onClick={handleLogout}
              aria-label="Logout"
              title="Logout"
            >
              🚪 Logout
            </button>
          )}
        </div>
      </header>
      
      <div className="main-container">
        {isMobile && sidebarOpen && (
          <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
        )}
        <nav className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
          <ul>
            <li><Link to="/">📊 Dashboard</Link></li>
            
            {(user?.role === 'admin' || user?.role === 'operator') && (
              <>
                <li><Link to="/customers">👥 Customers</Link></li>
                <li><Link to="/offerings">📅 Offerings</Link></li>
                <li><Link to="/orders">🥘 Orders</Link></li>
              </>
            )}
            
            {(user?.role === 'admin' || user?.role === 'cook') && (
              <li><Link to="/catalog">🍛 Menu</Link></li>
            )}
            
            {(user?.role === 'admin' || user?.role === 'operator') && (
              <li><Link to="/payments">💰 Payments</Link></li>
            )}
            
            {(user?.role === 'admin' || user?.role === 'operator') && (
              <>
                <li><Link to="/reports">📈 Reports</Link></li>
                <li><Link to="/analytics">🎯 Analytics</Link></li>
              </>
            )}
            
            {user?.role === 'admin' && (
              <>
                <li><Link to="/import">📥 Import</Link></li>
                <li><Link to="/google-sync">📊 Google Sync</Link></li>
                <li><Link to="/users">👤 Users</Link></li>
              </>
            )}
          </ul>
        </nav>
        
        <main className="content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;

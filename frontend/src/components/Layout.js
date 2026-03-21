import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Logo from './Logo';
import './Layout.css';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
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
        <button 
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label="Toggle theme"
          title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        >
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
      </header>
      
      <div className="main-container">
        <nav className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
          <ul>
            <li><Link to="/">Dashboard</Link></li>
            <li><Link to="/customers">Customers</Link></li>
            <li><Link to="/catalog">Catalog</Link></li>
            <li><Link to="/orders">Orders</Link></li>
            <li><Link to="/payments">Payments</Link></li>
            <li><Link to="/reports">Reports</Link></li>
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

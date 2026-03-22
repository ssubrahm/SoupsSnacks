import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';
import Customers from './pages/Customers';
import CustomerForm from './pages/CustomerForm';
import CustomerDetail from './pages/CustomerDetail';
import Products from './pages/Products';
import ProductForm from './pages/ProductForm';
import ProductDetail from './pages/ProductDetail';
import DailyOfferings from './pages/DailyOfferings';
import './App.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/customers"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <Customers />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/customers/new"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <CustomerForm />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/customers/:id"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <CustomerDetail />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/customers/:id/edit"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <CustomerForm />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/catalog"
            element={
              <ProtectedRoute requiredRole="cook">
                <Layout>
                  <Products />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/catalog/new"
            element={
              <ProtectedRoute requiredRole="cook">
                <Layout>
                  <ProductForm />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/catalog/:id"
            element={
              <ProtectedRoute requiredRole="cook">
                <Layout>
                  <ProductDetail />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/catalog/:id/edit"
            element={
              <ProtectedRoute requiredRole="cook">
                <Layout>
                  <ProductForm />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/offerings"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <DailyOfferings />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <div style={{ padding: '2rem' }}>
                    <h2>🥘 Orders</h2>
                    <p>Order management - Coming in Step 6</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/payments"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <div style={{ padding: '2rem' }}>
                    <h2>💰 Payments</h2>
                    <p>Payment tracking - Coming in Step 7</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <div style={{ padding: '2rem' }}>
                    <h2>📈 Reports</h2>
                    <p>Analytics and reports - Coming in Step 8</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/users"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <Users />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;

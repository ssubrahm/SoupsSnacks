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
import Orders from './pages/Orders';
import OrderForm from './pages/OrderForm';
import OrderDetail from './pages/OrderDetail';
import Payments from './pages/Payments';
import Reports from './pages/Reports';
import CustomerAnalytics from './pages/CustomerAnalytics';
import Import from './pages/Import';
import GoogleSync from './pages/GoogleSync';
import './styles/global.css';
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
                  <Orders />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders/new"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <OrderForm />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders/:id"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <OrderDetail />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders/:id/edit"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <OrderForm />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/payments"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <Payments />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <Reports />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute requiredRole="operator">
                <Layout>
                  <CustomerAnalytics />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/import"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <Import />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/google-sync"
            element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <GoogleSync />
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

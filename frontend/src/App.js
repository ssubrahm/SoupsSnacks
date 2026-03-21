import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/customers" element={<div>Customers - Coming Soon</div>} />
          <Route path="/catalog" element={<div>Catalog - Coming Soon</div>} />
          <Route path="/orders" element={<div>Orders - Coming Soon</div>} />
          <Route path="/payments" element={<div>Payments - Coming Soon</div>} />
          <Route path="/reports" element={<div>Reports - Coming Soon</div>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;

import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Users.css';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    role: 'operator'
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/accounts/users/');
      setUsers(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load users');
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/accounts/users/', formData);
      setShowCreateForm(false);
      setFormData({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        role: 'operator'
      });
      fetchUsers();
    } catch (err) {
      alert('Failed to create user: ' + (err.response?.data?.username || 'Unknown error'));
    }
  };

  const toggleUserStatus = async (userId, isActive) => {
    try {
      if (isActive) {
        await api.post(`/accounts/users/${userId}/deactivate/`);
      } else {
        await api.post(`/accounts/users/${userId}/activate/`);
      }
      fetchUsers();
    } catch (err) {
      alert('Failed to update user status');
    }
  };

  if (loading) return <div>Loading users...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="users-page">
      <div className="page-header">
        <h2>👤 User Management</h2>
        <button onClick={() => setShowCreateForm(!showCreateForm)} className="btn-primary">
          {showCreateForm ? 'Cancel' : '+ Add User'}
        </button>
      </div>

      {showCreateForm && (
        <div className="create-form-card">
          <h3>Create New User</h3>
          <form onSubmit={handleCreate} className="create-form">
            <div className="form-row">
              <div className="form-group">
                <label>Username *</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>First Name</label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Password *</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                  minLength={6}
                />
              </div>
              <div className="form-group">
                <label>Role *</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  required
                >
                  <option value="admin">Admin</option>
                  <option value="operator">Operator</option>
                  <option value="cook">Cook</option>
                </select>
              </div>
            </div>
            <button type="submit" className="btn-primary">Create User</button>
          </form>
        </div>
      )}

      <div className="users-table-card">
        <table className="users-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td><strong>{user.username}</strong></td>
                <td>{user.first_name} {user.last_name}</td>
                <td>{user.email}</td>
                <td>
                  <span className={`role-badge role-${user.role}`}>
                    {user.role}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  <button
                    onClick={() => toggleUserStatus(user.id, user.is_active)}
                    className="btn-secondary"
                  >
                    {user.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Users;

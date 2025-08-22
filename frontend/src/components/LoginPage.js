import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Scale, Users, Shield, Eye, EyeOff } from 'lucide-react';
import './LoginPage.css';

function LoginPage() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  
  const { login, loading } = useAuth();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear errors when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }
    
    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    const result = await login(formData.username, formData.password);
    
    if (!result.success) {
      setErrors({
        general: result.message || 'Login failed. Please check your credentials.'
      });
    }
  };

  return (
    <>
      <div className="logo-background"></div>
      <div className="login-page">
        <div className="login-container">
          <div className="login-card card">
            <div className="login-header">
              <div className="logo-section">
                <Scale size={48} className="logo-icon" />
                <h1 className="app-title">PRECEDENT</h1>
                <p className="app-subtitle">Legal Research & Analytics Platform</p>
              </div>
            </div>
            
            <div className="login-body card-body">
              <h2 className="login-title">Welcome Back</h2>
              <p className="login-description">
                Access your legal research tools and case analytics
              </p>
              
              {errors.general && (
                <div className="alert alert-error">
                  {errors.general}
                </div>
              )}
              
              <form onSubmit={handleSubmit} className="login-form">
                <div className="form-group">
                  <label htmlFor="username" className="form-label">
                    <Users size={18} />
                    Username
                  </label>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className={`form-control ${errors.username ? 'error' : ''}`}
                    placeholder="Enter your username"
                    disabled={loading}
                  />
                  {errors.username && (
                    <span className="error-message">{errors.username}</span>
                  )}
                </div>
                
                <div className="form-group">
                  <label htmlFor="password" className="form-label">
                    <Shield size={18} />
                    Password
                  </label>
                  <div className="password-input-container">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      className={`form-control ${errors.password ? 'error' : ''}`}
                      placeholder="Enter your password"
                      disabled={loading}
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowPassword(!showPassword)}
                      disabled={loading}
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  {errors.password && (
                    <span className="error-message">{errors.password}</span>
                  )}
                </div>
                
                <button
                  type="submit"
                  className="btn btn-primary login-btn"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <div className="loading-spinner"></div>
                      Signing In...
                    </>
                  ) : (
                    'Sign In'
                  )}
                </button>
              </form>
              
              <div className="login-footer">
                <div className="demo-credentials">
                  <h4>Demo Credentials:</h4>
                  <p><strong>Username:</strong> onebaldegg</p>
                  <p><strong>Password:</strong> 4life</p>
                </div>
                
                <div className="platform-info">
                  <h4>Platform Features:</h4>
                  <ul>
                    <li>Legal Decompiler - Plain language explanations</li>
                    <li>Analytics Engine - Statistical insights</li>
                    <li>Precedent Explorer - Case law search</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          
          <div className="platform-benefits">
            <div className="benefit-card">
              <Scale size={32} />
              <h3>Legal Clarity</h3>
              <p>Transform complex legal codes into understandable explanations</p>
            </div>
            
            <div className="benefit-card">
              <Users size={32} />
              <h3>Data-Driven Insights</h3>
              <p>Analyze historical case outcomes and judicial patterns</p>
            </div>
            
            <div className="benefit-card">
              <Shield size={32} />
              <h3>Comprehensive Research</h3>
              <p>Access relevant precedents and case law databases</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default LoginPage;
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Scale, LogOut, User, FileText, BarChart3, Search, Lightbulb, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../services/api';
import { toast } from 'react-toastify';
import './Dashboard.css';

function Dashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('form');
  const [formData, setFormData] = useState({
    crime_code: '',
    jurisdiction: '',
    additional_info: ''
  });
  const [loading, setLoading] = useState(false);
  const [confirmation, setConfirmation] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
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
    
    if (!formData.crime_code.trim()) {
      newErrors.crime_code = 'Crime/Penal Code is required';
    }
    
    if (!formData.jurisdiction.trim()) {
      newErrors.jurisdiction = 'Jurisdiction is required';
    }
    
    if (formData.additional_info && formData.additional_info.length > 1000) {
      newErrors.additional_info = 'Additional information must be 1000 characters or less';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmitForConfirmation = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      setLoading(true);
      const response = await api.post('/legal/confirm', formData);
      setConfirmation(response.data);
      setActiveTab('confirmation');
      toast.success('Please review and confirm your information');
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to process request';
      toast.error(errorMessage);
      console.error('Confirmation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmAndAnalyze = async () => {
    try {
      setLoading(true);
      setActiveTab('analyzing');
      
      const response = await api.post('/legal/analyze', formData);
      setAnalysis(response.data);
      setActiveTab('results');
      toast.success('Analysis completed successfully!');
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Analysis failed';
      toast.error(errorMessage);
      console.error('Analysis error:', error);
      setActiveTab('confirmation');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      crime_code: '',
      jurisdiction: '',
      additional_info: ''
    });
    setConfirmation(null);
    setAnalysis(null);
    setErrors({});
    setActiveTab('form');
  };

  const renderHeader = () => (
    <header className="dashboard-header">
      <div className="logo-background"></div>
      <div className="header-content">
        <div className="header-left">
          <Scale size={32} className="header-logo" />
          <div>
            <h1>PRECEDENT</h1>
            <p>Legal Research & Analytics Platform</p>
          </div>
        </div>
        <div className="header-right">
          <div className="user-info">
            <User size={20} />
            <span>Welcome, {user?.username}</span>
          </div>
          <button onClick={logout} className="btn btn-secondary logout-btn">
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </div>
    </header>
  );

  const renderForm = () => (
    <div className="analysis-form fade-in">
      <div className="form-header">
        <h2>Legal Case Analysis</h2>
        <p>Enter your case details for comprehensive legal research and analysis</p>
      </div>
      
      <form onSubmit={handleSubmitForConfirmation}>
        <div className="form-group">
          <label htmlFor="crime_code" className="form-label">
            <FileText size={18} />
            Crime / Penal Code *
          </label>
          <input
            type="text"
            id="crime_code"
            name="crime_code"
            value={formData.crime_code}
            onChange={handleInputChange}
            className={`form-control ${errors.crime_code ? 'error' : ''}`}
            placeholder="e.g., DUI, Vehicle Code § 23152, Penal Code § 240"
            disabled={loading}
          />
          {errors.crime_code && (
            <span className="error-message">{errors.crime_code}</span>
          )}
        </div>
        
        <div className="form-group">
          <label htmlFor="jurisdiction" className="form-label">
            <BarChart3 size={18} />
            Jurisdiction *
          </label>
          <input
            type="text"
            id="jurisdiction"
            name="jurisdiction"
            value={formData.jurisdiction}
            onChange={handleInputChange}
            className={`form-control ${errors.jurisdiction ? 'error' : ''}`}
            placeholder="e.g., Los Angeles County, California, Texas"
            disabled={loading}
          />
          {errors.jurisdiction && (
            <span className="error-message">{errors.jurisdiction}</span>
          )}
        </div>
        
        <div className="form-group">
          <label htmlFor="additional_info" className="form-label">
            <Search size={18} />
            Additional Information
            <span className="optional-label">(Optional - Up to 1000 characters)</span>
          </label>
          <textarea
            id="additional_info"
            name="additional_info"
            value={formData.additional_info}
            onChange={handleInputChange}
            className={`form-control ${errors.additional_info ? 'error' : ''}`}
            placeholder="Provide any specific details about your case, circumstances, or questions you have. This information will help our AI provide more accurate and relevant analysis."
            rows="6"
            maxLength="1000"
            disabled={loading}
          />
          <div className="character-count">
            {formData.additional_info.length}/1000 characters
          </div>
          {errors.additional_info && (
            <span className="error-message">{errors.additional_info}</span>
          )}
        </div>
        
        <button
          type="submit"
          className="btn btn-primary submit-btn"
          disabled={loading}
        >
          {loading ? (
            <>
              <div className="loading-spinner"></div>
              Processing...
            </>
          ) : (
            <>
              <Lightbulb size={18} />
              Analyze Case
            </>
          )}
        </button>
      </form>
    </div>
  );

  const renderConfirmation = () => (
    <div className="confirmation-section fade-in">
      <div className="confirmation-header">
        <AlertCircle size={32} className="confirmation-icon" />
        <h2>Confirm Your Information</h2>
        <p>Please review the details before proceeding with analysis</p>
      </div>
      
      {confirmation && (
        <div className="confirmation-content">
          <div className="confirmation-summary">
            <h3>AI Analysis Summary:</h3>
            <p>{confirmation.summary}</p>
          </div>
          
          <div className="confirmation-details">
            <h3>Key Details:</h3>
            <ul>
              {confirmation.key_details.map((detail, index) => (
                <li key={index}>
                  <CheckCircle size={16} />
                  {detail}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="confirmation-questions">
            <h3>Please Verify:</h3>
            <ul>
              {confirmation.questions.map((question, index) => (
                <li key={index}>{question}</li>
              ))}
            </ul>
          </div>
          
          <div className="confirmation-next">
            <h3>Next Steps:</h3>
            <p>{confirmation.next_steps}</p>
          </div>
          
          <div className="confirmation-actions">
            <button
              onClick={() => setActiveTab('form')}
              className="btn btn-secondary"
              disabled={loading}
            >
              Back to Edit
            </button>
            <button
              onClick={handleConfirmAndAnalyze}
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="loading-spinner"></div>
                  Analyzing...
                </>
              ) : (
                'Proceed with Analysis'
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );

  const renderAnalyzing = () => (
    <div className="analyzing-section fade-in">
      <div className="analyzing-content">
        <div className="analyzing-spinner">
          <div className="large-spinner"></div>
        </div>
        <h2>Analyzing Your Case</h2>
        <p>Our AI agents are working together to provide comprehensive analysis...</p>
        
        <div className="progress-steps">
          <div className="step active">
            <FileText size={20} />
            <span>Legal Decompiler</span>
          </div>
          <div className="step active">
            <BarChart3 size={20} />
            <span>Analytics Engine</span>
          </div>
          <div className="step active">
            <Search size={20} />
            <span>Precedent Explorer</span>
          </div>
        </div>
        
        <div className="analyzing-details">
          <p>🔍 Analyzing legal code and statutes...</p>
          <p>📊 Processing historical case data...</p>
          <p>⚖️ Searching relevant precedents...</p>
          <p>🤝 Synthesizing comprehensive analysis...</p>
        </div>
      </div>
    </div>
  );

  const renderResults = () => (
    <div className="results-section fade-in">
      {analysis && (
        <>
          <div className="results-header">
            <CheckCircle size={32} className="success-icon" />
            <h2>Analysis Complete</h2>
            <p>Comprehensive legal analysis for your case</p>
          </div>
          
          <div className="results-content">
            {/* Legal Explanation */}
            <div className="result-card">
              <div className="result-card-header">
                <FileText size={24} />
                <h3>Legal Decompiler</h3>
              </div>
              <div className="result-card-content">
                {analysis.legal_explanation && (
                  <>
                    <h4>{analysis.legal_explanation.crime_name}</h4>
                    <p className="simple-explanation">{analysis.legal_explanation.simple_explanation}</p>
                    
                    <div className="legal-details">
                      <div className="detail-section">
                        <h5>What the Prosecution Must Prove:</h5>
                        <ul>
                          {analysis.legal_explanation.what_prosecution_must_prove?.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      </div>
                      
                      <div className="detail-section">
                        <h5>Potential Penalties:</h5>
                        <div className="penalties">
                          {Object.entries(analysis.legal_explanation.penalties || {}).map(([type, penalty]) => (
                            <div key={type} className="penalty-type">
                              <strong>{type.replace('_', ' ').toUpperCase()}:</strong>
                              {typeof penalty === 'object' ? (
                                <ul>
                                  {Object.entries(penalty).map(([key, value]) => (
                                    <li key={key}><strong>{key.replace('_', ' ')}:</strong> {value}</li>
                                  ))}
                                </ul>
                              ) : (
                                <span>{penalty}</span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
            
            {/* Analytics */}
            <div className="result-card">
              <div className="result-card-header">
                <BarChart3 size={24} />
                <h3>Analytics Engine</h3>
              </div>
              <div className="result-card-content">
                {analysis.analytics && (
                  <>
                    <div className="analytics-stats">
                      <div className="stat-item">
                        <span className="stat-value">{analysis.analytics.jurisdiction_stats?.total_cases_last_year}</span>
                        <span className="stat-label">Cases Last Year</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-value">{analysis.analytics.jurisdiction_stats?.conviction_rate}%</span>
                        <span className="stat-label">Conviction Rate</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-value">{analysis.analytics.success_rates?.dismissal}%</span>
                        <span className="stat-label">Dismissal Rate</span>
                      </div>
                    </div>
                    
                    <div className="common-defenses">
                      <h5>Common Defense Strategies:</h5>
                      {analysis.analytics.common_defenses?.map((defense, index) => (
                        <div key={index} className="defense-item">
                          <strong>{defense.strategy}</strong>
                          <div className="defense-stats">
                            <span>Success Rate: {defense.success_rate}%</span>
                            <span>Frequency: {defense.frequency}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>
            
            {/* Precedents */}
            <div className="result-card">
              <div className="result-card-header">
                <Search size={24} />
                <h3>Precedent Explorer</h3>
              </div>
              <div className="result-card-content">
                {analysis.precedents && (
                  <>
                    <p className="cases-found">{analysis.precedents.total_cases_found} relevant cases found</p>
                    
                    <div className="precedent-cases">
                      {analysis.precedents.cases?.map((case_item, index) => (
                        <div key={index} className="case-item">
                          <div className="case-header">
                            <h5>{case_item.case_name}</h5>
                            <span className="relevance-score">{case_item.relevance_score}% relevant</span>
                          </div>
                          <div className="case-details">
                            <p><strong>Key Issue:</strong> {case_item.key_issue}</p>
                            <p><strong>Outcome:</strong> {case_item.outcome}</p>
                            <p><strong>Summary:</strong> {case_item.summary}</p>
                            <p><strong>Legal Principle:</strong> {case_item.legal_principle}</p>
                            <p><strong>Citation:</strong> {case_item.citation}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>
            
            {/* Summary */}
            {analysis.summary && (
              <div className="result-card summary-card">
                <div className="result-card-header">
                  <Lightbulb size={24} />
                  <h3>Executive Summary</h3>
                </div>
                <div className="result-card-content">
                  <div className="key-points">
                    <h5>Key Points:</h5>
                    <ul>
                      {analysis.summary.key_points?.map((point, index) => (
                        <li key={index}>{point}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="recommended-actions">
                    <h5>Recommended Actions:</h5>
                    <ul>
                      {analysis.summary.recommended_actions?.map((action, index) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
            
            <div className="results-actions">
              <button
                onClick={resetForm}
                className="btn btn-primary"
              >
                New Analysis
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );

  return (
    <>
      <div className="logo-background"></div>
      <div className="dashboard">
        {renderHeader()}
        
        <main className="dashboard-main content-overlay">
          <div className="container">
            {activeTab === 'form' && renderForm()}
            {activeTab === 'confirmation' && renderConfirmation()}
            {activeTab === 'analyzing' && renderAnalyzing()}
            {activeTab === 'results' && renderResults()}
          </div>
        </main>
      </div>
    </>
  );
}

export default Dashboard;
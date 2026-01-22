import React, { useState } from 'react';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setError('Please enter some text to parse');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/parse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          llm: 'gpt-4o-mini'
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(`Failed to parse contact information: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>📇 Contact Information Parser</h1>
          <p className="subtitle">Extract contact details from natural language text</p>
        </header>

        <div className="main-content">
          <form onSubmit={handleSubmit} className="input-section">
            <label htmlFor="text-input" className="input-label">
              Enter text containing contact information:
            </label>
            <textarea
              id="text-input"
              className="text-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Example: Contact Jane Doe at jane.doe@global.com, phone: 555-234-5678"
              rows="6"
              disabled={loading}
            />
            <div className="button-group">
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Parsing...' : 'Parse Contact'}
              </button>
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={handleClear}
                disabled={loading}
              >
                Clear
              </button>
            </div>
          </form>

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Extracting contact information...</p>
            </div>
          )}

          {error && (
            <div className="error-message">
              <div className="error-icon">⚠️</div>
              <p>{error}</p>
            </div>
          )}

          {result && !loading && (
            <div className="results-section">
              <h2 className="results-title">Extracted Information</h2>
              <div className="result-card">
                <div className="result-row">
                  <span className="result-label">Name:</span>
                  <span className="result-value">{result.name || 'Not found'}</span>
                </div>
                <div className="result-row">
                  <span className="result-label">Email:</span>
                  <span className="result-value">{result.email || 'Not found'}</span>
                </div>
                <div className="result-row">
                  <span className="result-label">Phone:</span>
                  <span className="result-value">{result.phone || 'Not found'}</span>
                </div>
                <div className="result-row">
                  <span className="result-label">Database Status:</span>
                  <span className={`result-badge ${result.found_in_database ? 'found' : 'not-found'}`}>
                    {result.found_in_database ? '✓ Found in database' : '✗ Not found in database'}
                  </span>
                </div>
                {result.found_in_database && result.company && (
                  <div className="result-row">
                    <span className="result-label">Company:</span>
                    <span className="result-value company">{result.company}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <footer className="footer">
          <p>Powered by AI • Backend running on http://localhost:8000</p>
        </footer>
      </div>
    </div>
  );
}

export default App;

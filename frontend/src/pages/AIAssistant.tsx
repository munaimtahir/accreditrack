import React, { useState } from 'react';
import { aiService } from '../services/api';

/**
 * The AI Assistant page component.
 *
 * This component provides a user interface for interacting with the AI Compliance Assistant.
 * It allows users to ask questions and view the AI-generated responses.
 *
 * @state
 * @property {string} question - Stores the user's input question.
 * @property {string} response - Stores the response from the AI or any error messages.
 * @property {boolean} loading - Tracks the loading state of the API request.
 *
 * @returns {React.ReactElement} The rendered AI Assistant page.
 */
const AIAssistant: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  /**
   * Handles the form submission for asking the AI assistant a question.
   *
   * @param {React.FormEvent} e The form event.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResponse('');

    try {
      const res = await aiService.askAssistant(question);
      setResponse(res.data.result || res.data.error || 'No response received');
    } catch (err: any) {
      setResponse(`Error: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>AI Compliance Assistant</h1>
      <p>Ask questions about compliance, regulations, and accreditation standards.</p>

      <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>Your Question:</label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            style={{ width: '100%', padding: '10px', minHeight: '100px' }}
            placeholder="e.g., What are the key requirements for PMDC accreditation?"
            required
          />
        </div>
        <button 
          type="submit" 
          disabled={loading}
          style={{ padding: '10px 20px', cursor: loading ? 'not-allowed' : 'pointer' }}
        >
          {loading ? 'Processing...' : 'Ask AI'}
        </button>
      </form>

      {response && (
        <div style={{ marginTop: '30px', padding: '20px', border: '1px solid #ccc', borderRadius: '5px', backgroundColor: '#f9f9f9' }}>
          <h3>Response:</h3>
          <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>{response}</pre>
        </div>
      )}

      <div style={{ marginTop: '40px', padding: '20px', border: '1px solid #e0e0e0', borderRadius: '5px' }}>
        <h3>Other AI Features Available:</h3>
        <ul>
          <li>Analyze Checklist - Analyze compliance checklists</li>
          <li>Categorize Indicators - Group indicators logically</li>
          <li>Generate Summary - Create compliance reports</li>
          <li>Convert Documents - Transform document formats</li>
          <li>Compliance Guide - Get guides for specific standards</li>
          <li>Analyze Tasks - Optimize compliance tasks</li>
        </ul>
        <p style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>
          Note: These features require a valid Gemini API key to be configured.
        </p>
      </div>
    </div>
  );
};

export default AIAssistant;

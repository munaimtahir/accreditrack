import React from 'react';
import { Link } from 'react-router-dom';

/**
 * The main dashboard component for the application.
 *
 * This component serves as the landing page after login, providing an overview
 * of the platform and quick links to the major sections like Projects,
 * Indicators, and the AI Assistant.
 *
 * @returns {React.ReactElement} The rendered dashboard page.
 */
const Dashboard: React.FC = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>AccrediFy Dashboard</h1>
      <p>Welcome to the Compliance and Accreditation Management Platform</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginTop: '30px' }}>
        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <h3>Projects</h3>
          <p>Manage accreditation projects</p>
          <Link to="/projects">
            <button style={{ marginTop: '10px', padding: '10px 20px' }}>View Projects</button>
          </Link>
        </div>

        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <h3>Indicators</h3>
          <p>Track compliance indicators</p>
          <Link to="/indicators">
            <button style={{ marginTop: '10px', padding: '10px 20px' }}>View Indicators</button>
          </Link>
        </div>

        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <h3>AI Assistant</h3>
          <p>Get AI-powered compliance help</p>
          <Link to="/ai-assistant">
            <button style={{ marginTop: '10px', padding: '10px 20px' }}>Ask AI</button>
          </Link>
        </div>
      </div>

      <div style={{ marginTop: '40px', padding: '20px', backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
        <h2>About AccrediFy</h2>
        <p>
          AccrediFy is a comprehensive compliance and accreditation management platform designed for 
          medical institutions, laboratories, and universities. It helps you:
        </p>
        <ul>
          <li>Create and manage accreditation projects (PHC Lab, PMDC, CPSP, etc.)</li>
          <li>Track indicators and requirements with detailed checklists</li>
          <li>Upload and link evidence documentation</li>
          <li>Monitor compliance progress and status</li>
          <li>Use AI assistance for analysis and guidance</li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;

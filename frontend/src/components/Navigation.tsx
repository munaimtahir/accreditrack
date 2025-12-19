import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

/**
 * Navigation component for the application.
 *
 * This component renders the main navigation bar, which is visible only to
 * authenticated users. It includes links to the main sections of the application
 * and a logout button.
 *
 * @returns {React.ReactElement|null} The navigation bar component or null if the user is not authenticated.
 */
const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const isAuthenticated = authService.isAuthenticated();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <nav style={{ 
      padding: '15px 20px', 
      backgroundColor: '#333', 
      color: 'white',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
        <Link to="/" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold', fontSize: '18px' }}>
          AccrediFy
        </Link>
        <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Dashboard</Link>
        <Link to="/projects" style={{ color: 'white', textDecoration: 'none' }}>Projects</Link>
        <Link to="/indicators" style={{ color: 'white', textDecoration: 'none' }}>Indicators</Link>
        <Link to="/ai-assistant" style={{ color: 'white', textDecoration: 'none' }}>AI Assistant</Link>
      </div>
      <button 
        onClick={handleLogout}
        style={{ 
          padding: '8px 16px', 
          backgroundColor: '#555', 
          color: 'white', 
          border: 'none',
          cursor: 'pointer',
          borderRadius: '4px'
        }}
      >
        Logout
      </button>
    </nav>
  );
};

export default Navigation;

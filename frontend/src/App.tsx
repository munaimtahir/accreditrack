import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navigation from './components/Navigation';
import PrivateRoute from './components/PrivateRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Indicators from './pages/Indicators';
import AIAssistant from './pages/AIAssistant';
import EvidenceLibrary from './pages/EvidenceLibrary';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
        <Navigation />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route 
            path="/" 
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/projects" 
            element={
              <PrivateRoute>
                <Projects />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/indicators" 
            element={
              <PrivateRoute>
                <Indicators />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/ai-assistant" 
            element={
              <PrivateRoute>
                <AIAssistant />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/projects/:projectId/evidence" 
            element={
              <PrivateRoute>
                <EvidenceLibrary />
              </PrivateRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;

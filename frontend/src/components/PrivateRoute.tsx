import React from 'react';
import { Navigate } from 'react-router-dom';
import { authService } from '../services/api';

interface PrivateRouteProps {
  children: React.ReactNode;
}

/**
 * A component that renders its children only if the user is authenticated.
 *
 * If the user is not authenticated, they are redirected to the login page.
 *
 * @param {PrivateRouteProps} props The props for the component.
 * @param {React.ReactNode} props.children The child components to render if authenticated.
 * @returns {React.ReactElement} The child components or a redirect to the login page.
 */
const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default PrivateRoute;

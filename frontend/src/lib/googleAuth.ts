/**
 * Google OAuth Authentication for Drive API
 * Handles user authentication and token management
 */

import './googleTypes';

const GOOGLE_CLIENT_ID = '1068296249769-u9uoaiq6tm8sp8j94mho7grhmdef3ji5.apps.googleusercontent.com';
const SCOPES = 'https://www.googleapis.com/auth/drive.file';

let tokenClient: any = null;

/**
 * Initialize Google OAuth client
 */
const initTokenClient = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // Check if Google Identity Services script is loaded
    if (typeof window.google === 'undefined' || !window.google.accounts) {
      // Load the Google Identity Services script
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Google Identity Services'));
      document.head.appendChild(script);
    } else {
      resolve();
    }
  });
};

/**
 * Get Drive access token
 * Prompts user for authentication if needed
 */
export const getDriveAccessToken = async (): Promise<string> => {
  // Ensure Google Identity Services is loaded
  await initTokenClient();

  return new Promise((resolve, reject) => {
    try {
      tokenClient = window.google.accounts.oauth2.initTokenClient({
        client_id: GOOGLE_CLIENT_ID,
        scope: SCOPES,
        callback: (response) => {
          if (response.error) {
            reject(new Error(response.error));
            return;
          }
          resolve(response.access_token);
        },
      });

      tokenClient.requestAccessToken();
    } catch (error) {
      reject(error);
    }
  });
};

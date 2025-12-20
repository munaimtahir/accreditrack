/**
 * Google Drive Folder Picker
 * Allows users to select folders from their Drive
 */

import './googleTypes';

const GOOGLE_API_KEY = 'AIzaSyDETkPOeeknQgGyLGQOwgsvDgguFGtve4Q';
const APP_ID = '1068296249769';

/**
 * Load Google Picker API
 */
const loadPickerApi = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // Check if already loaded
    if (window.gapi && window.google && window.google.picker) {
      resolve();
      return;
    }

    // Load gapi script
    const script = document.createElement('script');
    script.src = 'https://apis.google.com/js/api.js';
    script.async = true;
    script.defer = true;
    script.onload = () => {
      window.gapi.load('picker', {
        callback: () => {
          window.gapi.client.setApiKey(GOOGLE_API_KEY);
          resolve();
        },
        onerror: () => reject(new Error('Failed to load Google Picker API')),
      });
    };
    script.onerror = () => reject(new Error('Failed to load GAPI script'));
    document.head.appendChild(script);
  });
};

export interface PickerResult {
  folderId: string;
  folderName: string;
}

/**
 * Open Google Drive folder picker
 * @param accessToken OAuth access token
 * @returns Promise with selected folder information
 */
export const pickFolder = async (accessToken: string): Promise<PickerResult> => {
  // Load picker API if needed
  await loadPickerApi();

  return new Promise((resolve, reject) => {
    try {
      // Create a folder view - FOLDERS ViewId already shows folders
      const view = new window.google.picker.DocsView(window.google.picker.ViewId.FOLDERS);

      const picker = new window.google.picker.PickerBuilder()
        .setAppId(APP_ID)
        .setOAuthToken(accessToken)
        .addView(view)
        .setDeveloperKey(GOOGLE_API_KEY)
        .setCallback((data: any) => {
          if (data.action === window.google.picker.Action.PICKED) {
            const folder = data.docs[0];
            resolve({
              folderId: folder.id,
              folderName: folder.name,
            });
          } else if (data.action === window.google.picker.Action.CANCEL) {
            reject(new Error('Folder selection cancelled'));
          }
        })
        .setTitle('Select Google Drive Folder')
        .build();

      picker.setVisible(true);
    } catch (error) {
      reject(error);
    }
  });
};

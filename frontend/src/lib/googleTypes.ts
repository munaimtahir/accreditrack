/**
 * Global type declarations for Google APIs
 */

declare global {
  interface Window {
    // Google Identity Services (OAuth 2.0)
    google: {
      accounts: {
        oauth2: {
          initTokenClient: (config: {
            client_id: string;
            scope: string;
            callback: (response: { access_token: string; error?: string }) => void;
          }) => {
            requestAccessToken: () => void;
          };
        };
      };
      // Google Picker API
      picker: {
        DocsView: any;
        ViewId: {
          FOLDERS: string;
        };
        PickerBuilder: new () => {
          setAppId: (appId: string) => any;
          setOAuthToken: (token: string) => any;
          addView: (view: any) => any;
          setDeveloperKey: (key: string) => any;
          setCallback: (callback: (data: any) => void) => any;
          setTitle: (title: string) => any;
          enableFeature: (feature: any) => any;
          build: () => {
            setVisible: (visible: boolean) => void;
          };
        };
        Feature: {
          MULTISELECT_ENABLED: any;
          NAV_HIDDEN: any;
        };
        Action: {
          PICKED: string;
          CANCEL: string;
        };
      };
    };
    // Google API Client
    gapi: {
      load: (api: string, options: { callback: () => void; onerror?: () => void }) => void;
      client: {
        setApiKey: (key: string) => void;
      };
    };
  }
}

export {};

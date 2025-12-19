# Google Drive Integration Deployment Guide

This document explains how to deploy and configure the Google Drive integration for AccrediFy.

## Overview

The Google Drive integration allows projects to link to Google Drive folders and automatically organize evidence files in a structured folder hierarchy:
- `ProjectFolder/SectionName/StandardName/`

Evidence files are uploaded directly to Google Drive from the browser, and only metadata is stored in the backend database.

## Prerequisites

1. **Google Cloud Console Setup**
   - Enabled Google Drive API
   - Created OAuth Client ID (Web Application)
   - Created API Key
   - Configured authorized JavaScript origins:
     - `https://accredify.pmc.edu.pk`
     - `http://accredify.pmc.edu.pk`
     - `http://172.104.187.212` (temporary IP access)
     - `http://172.104.187.212:80`
     - `http://172.104.187.212:5173` (dev server)

2. **OAuth Client Credentials**
   - Client ID: `1068296249769-u9uoaiq6tm8sp8j94mho7grhmdef3ji5.apps.googleusercontent.com`
   - API Key: `AIzaSyDETkPOeeknQgGyLGQOwgsvDgguFGtve4Q`

## Frontend Configuration

### Environment Variables

Create or update `frontend/.env` (or `.env.production` for production):

```bash
VITE_GOOGLE_CLIENT_ID=1068296249769-u9uoaiq6tm8sp8j94mho7grhmdef3ji5.apps.googleusercontent.com
VITE_GOOGLE_API_KEY=AIzaSyDETkPOeeknQgGyLGQOwgsvDgguFGtve4Q
```

**Note:** These values are already hardcoded in the frontend code, but environment variables allow for easy configuration changes.

### Build and Deploy

```bash
cd frontend
npm install
npm run build
```

The built files will be in `frontend/dist/` and should be served by your web server (nginx).

## Backend Configuration

### CORS Settings

The backend CORS settings are already configured in `backend/accredify_backend/settings.py` to allow:
- `https://accredify.pmc.edu.pk`
- `http://accredify.pmc.edu.pk`
- `http://172.104.187.212`
- `http://172.104.187.212:80`
- `http://172.104.187.212:5173`

If you need to add more origins, update the `CORS_ALLOWED_ORIGINS` setting.

### Database Migration

Run the migration to add Drive integration fields:

```bash
cd backend
python manage.py migrate
```

This will create the following fields:
- `Project.drive_folder_id`
- `Project.evidence_storage_mode`
- `Project.drive_linked_at`
- `Project.drive_linked_email`
- `Evidence.storage`
- `Evidence.drive_file_id`
- `Evidence.drive_web_view_link`
- `Evidence.drive_mime_type`
- `Evidence.original_filename`
- `Evidence.project` (FK)

## Testing

### 1. Link a Drive Folder

1. Navigate to a project page
2. Click "Link Google Drive Folder"
3. Sign in with Google (if not already signed in)
4. Select a folder from Google Drive
5. The folder should be linked and `evidence_storage_mode` should change to `gdrive`

### 2. Upload Evidence

1. Navigate to an indicator with evidence upload enabled
2. Click "Add Evidence"
3. Select a file and fill in the form
4. Click "Submit Evidence"
5. The file should be uploaded to: `ProjectFolder/SectionName/StandardName/`
6. Evidence record should show "Open in Drive" link

### 3. Verify Folder Structure

1. Open Google Drive
2. Navigate to the linked project folder
3. Verify folder structure:
   ```
   ProjectFolder/
   ├── Section A/
   │   ├── Standard 1/
   │   │   └── evidence_file.pdf
   │   └── Standard 2/
   └── Section B/
   ```

### 4. Unlink Drive Folder

1. Navigate to project page
2. Click "Unlink Drive Folder"
3. Confirm the action
4. `evidence_storage_mode` should change back to `local`
5. Future uploads will use local storage

## Domain vs IP Access

**Important:** Google OAuth works best when accessing the app via the domain (`accredify.pmc.edu.pk`). 

When accessing via IP address (`172.104.187.212`):
- The UI will display correctly
- Google login/Picker may fail if the OAuth origin doesn't match allowed domains
- The app shows a warning message when accessed via IP

**Recommendation:** Use the domain for production access. IP access is kept in CORS/config for development/testing purposes.

## Troubleshooting

### OAuth Not Working

1. Check that the domain is in the authorized JavaScript origins in Google Cloud Console
2. Verify `VITE_GOOGLE_CLIENT_ID` is set correctly
3. Check browser console for errors
4. Ensure you're accessing via the configured domain (not just IP)

### Folder Picker Not Showing

1. Verify `VITE_GOOGLE_API_KEY` is set correctly
2. Check that Google Picker API is enabled in Google Cloud Console
3. Check browser console for errors
4. Ensure access token is valid

### File Upload Fails

1. Check that the project has a linked Drive folder
2. Verify the user has write permissions to the Drive folder
3. Check browser console for detailed error messages
4. Ensure the access token hasn't expired (tokens expire after 1 hour)

### Folder Structure Not Created

1. Verify the user has permission to create folders in the Drive folder
2. Check that section/standard names are valid (no invalid characters)
3. Check browser console for errors

## Security Notes

1. **No Backend Tokens:** OAuth tokens are never stored in the backend. All authentication happens in the browser.
2. **Minimal Scopes:** The integration uses `https://www.googleapis.com/auth/drive.file` scope, which only allows access to files created by the app.
3. **Token Expiry:** Access tokens expire after 1 hour. Users will be prompted to re-authenticate when needed.

## API Endpoints

### Link Drive Folder
```
POST /api/projects/{id}/link-drive-folder/
Body: {
  "drive_folder_id": "1AbC...",
  "drive_linked_email": "user@gmail.com"  // optional
}
```

### Unlink Drive Folder
```
POST /api/projects/{id}/unlink-drive-folder/
```

### Get Project Evidence
```
GET /api/projects/{id}/evidence/
```

### Create Evidence (Drive)
```
POST /api/evidence/
Body: {
  "project": 1,
  "indicator": 10,
  "storage": "gdrive",
  "title": "Policy document",
  "original_filename": "policy.pdf",
  "drive_file_id": "1XYZ...",
  "drive_web_view_link": "https://drive.google.com/file/d/1XYZ/view",
  "drive_mime_type": "application/pdf"
}
```

## Support

For issues or questions:
1. Check browser console for errors
2. Check backend logs for API errors
3. Verify Google Cloud Console configuration
4. Ensure all environment variables are set correctly


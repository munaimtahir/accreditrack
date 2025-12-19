"""
Google Drive Integration Service for Evidence Library.

Handles OAuth 2.0 authentication, folder creation, file uploads, and sharing links.
"""
import os
import json
from typing import Optional, Dict, Tuple
from django.conf import settings
from django.utils import timezone
from .models import Project, Indicator, GoogleDriveFolderCache

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
    from googleapiclient.errors import HttpError
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False


# OAuth 2.0 scopes required for Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_oauth_flow(redirect_uri: str) -> Optional[Flow]:
    """
    Create OAuth 2.0 flow for Google Drive authentication.
    
    Args:
        redirect_uri: Redirect URI after OAuth consent
        
    Returns:
        Flow object or None if credentials not configured
    """
    if not GOOGLE_DRIVE_AVAILABLE:
        return None
    
    client_id = os.getenv('GOOGLE_DRIVE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_DRIVE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        return None
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        },
        scopes=SCOPES
    )
    
    return flow


def get_drive_service(project: Project):
    """
    Get authenticated Google Drive service for a project.
    
    Args:
        project: Project instance with OAuth token
        
    Returns:
        Google Drive service object or None
    """
    if not GOOGLE_DRIVE_AVAILABLE:
        return None
    
    if not project.google_drive_oauth_token:
        return None
    
    try:
        creds = Credentials.from_authorized_user_info(
            json.loads(project.google_drive_oauth_token) if isinstance(project.google_drive_oauth_token, str) 
            else project.google_drive_oauth_token
        )
        
        # Refresh token if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token
            project.google_drive_oauth_token = json.loads(creds.to_json())
            project.save(update_fields=['google_drive_oauth_token'])
        
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error creating Drive service: {e}")
        return None


def initialize_project_drive_folder(project: Project) -> Optional[str]:
    """
    Initialize Google Drive root folder for a project.
    Creates folder if it doesn't exist, returns folder ID.
    
    Args:
        project: Project instance
        
    Returns:
        Google Drive folder ID or None
    """
    if project.google_drive_root_folder_id:
        # Verify folder still exists
        service = get_drive_service(project)
        if service:
            try:
                service.files().get(fileId=project.google_drive_root_folder_id).execute()
                return project.google_drive_root_folder_id
            except HttpError:
                # Folder doesn't exist, create new one
                pass
    
    service = get_drive_service(project)
    if not service:
        return None
    
    try:
        folder_metadata = {
            'name': f"AccrediFy - {project.name}",
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        
        folder_id = folder.get('id')
        
        # Save folder ID to project
        project.google_drive_root_folder_id = folder_id
        if not project.google_drive_linked_at:
            project.google_drive_linked_at = timezone.now()
        project.save(update_fields=['google_drive_root_folder_id', 'google_drive_linked_at'])
        
        return folder_id
    except HttpError as e:
        print(f"Error creating Drive folder: {e}")
        return None


def ensure_indicator_folder_structure(indicator: Indicator) -> Optional[Dict[str, str]]:
    """
    Ensure folder structure exists for an indicator.
    Creates: Section/Standard Code - Standard Name/Indicator Code - Indicator Title/
    
    Returns dict with folder IDs:
    {
        'root': root_folder_id,
        'section': section_folder_id,
        'standard': standard_folder_id,
        'indicator': indicator_folder_id,
        'uploads': uploads_folder_id,
        'logs': logs_folder_id,
        'forms': forms_folder_id,
        'images': images_folder_id,
        'videos': videos_folder_id
    }
    
    Args:
        indicator: Indicator instance
        
    Returns:
        Dict with folder IDs or None
    """
    project = indicator.project
    root_folder_id = initialize_project_drive_folder(project)
    if not root_folder_id:
        return None
    
    service = get_drive_service(project)
    if not service:
        return None
    
    # Build folder path
    section_name = indicator.section.name if indicator.section else (indicator.area or 'Uncategorized')
    standard_name = indicator.standard.name if indicator.standard else (indicator.regulation_or_standard or 'Uncategorized')
    indicator_title = indicator.requirement[:50]  # Truncate for folder name
    indicator_code = indicator.indicator_code or f"IND-{indicator.id}"
    
    # Create folder path string for cache lookup
    folder_path_parts = [
        section_name,
        f"{indicator_code} - {indicator_title}"
    ]
    if indicator.standard:
        folder_path = f"{section_name}/{indicator_code} - {indicator_title}"
    else:
        folder_path = f"{section_name}/{indicator_code} - {indicator_title}"
    
    # Check cache first
    cache_key = f"{section_name}/{standard_name}/{indicator_code} - {indicator_title}"
    cached = GoogleDriveFolderCache.objects.filter(
        project=project,
        folder_path=cache_key
    ).first()
    
    if cached:
        # Verify folder exists
        try:
            service.files().get(fileId=cached.google_drive_folder_id).execute()
            indicator_folder_id = cached.google_drive_folder_id
        except HttpError:
            cached = None
    
    folder_ids = {'root': root_folder_id}
    
    # Create section folder
    section_folder_id = _get_or_create_folder(
        service, root_folder_id, section_name, project, f"{section_name}"
    )
    folder_ids['section'] = section_folder_id
    
    # Create standard folder
    standard_folder_name = f"{indicator_code} - {standard_name}"
    standard_folder_id = _get_or_create_folder(
        service, section_folder_id, standard_folder_name, project,
        f"{section_name}/{standard_folder_name}"
    )
    folder_ids['standard'] = standard_folder_id
    
    # Create indicator folder
    indicator_folder_name = f"{indicator_code} - {indicator_title}"
    indicator_folder_id = _get_or_create_folder(
        service, standard_folder_id, indicator_folder_name, project,
        cache_key
    )
    folder_ids['indicator'] = indicator_folder_id
    
    # Create subfolders
    subfolders = ['uploads', 'logs', 'forms', 'images', 'videos']
    for subfolder_name in subfolders:
        subfolder_id = _get_or_create_folder(
            service, indicator_folder_id, subfolder_name, project,
            f"{cache_key}/{subfolder_name}"
        )
        folder_ids[subfolder_name] = subfolder_id
    
    return folder_ids


def _get_or_create_folder(
    service, parent_id: str, folder_name: str, project: Project, cache_path: str
) -> Optional[str]:
    """
    Get existing folder or create it. Uses cache for idempotency.
    
    Args:
        service: Google Drive service
        parent_id: Parent folder ID
        folder_name: Name of folder to create/get
        project: Project instance
        cache_path: Path for cache lookup
        
    Returns:
        Folder ID or None
    """
    # Check cache
    cached = GoogleDriveFolderCache.objects.filter(
        project=project,
        folder_path=cache_path
    ).first()
    
    if cached:
        try:
            # Verify folder exists
            service.files().get(fileId=cached.google_drive_folder_id).execute()
            return cached.google_drive_folder_id
        except HttpError:
            # Folder doesn't exist, delete cache entry
            cached.delete()
    
    # Check if folder exists in Drive
    try:
        results = service.files().list(
            q=f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields='files(id, name)'
        ).execute()
        
        items = results.get('files', [])
        if items:
            folder_id = items[0]['id']
            # Cache it
            GoogleDriveFolderCache.objects.update_or_create(
                project=project,
                folder_path=cache_path,
                defaults={'google_drive_folder_id': folder_id}
            )
            return folder_id
    except HttpError:
        pass
    
    # Create folder
    try:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        
        folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        
        folder_id = folder.get('id')
        
        # Cache it
        GoogleDriveFolderCache.objects.update_or_create(
            project=project,
            folder_path=cache_path,
            defaults={'google_drive_folder_id': folder_id}
        )
        
        return folder_id
    except HttpError as e:
        print(f"Error creating folder '{folder_name}': {e}")
        return None


def upload_file_to_drive(
    file_obj, folder_id: str, indicator: Indicator, file_name: Optional[str] = None
) -> Optional[Dict[str, str]]:
    """
    Upload file to Google Drive in the specified folder.
    
    Args:
        file_obj: File object or file path
        folder_id: Google Drive folder ID
        indicator: Indicator instance
        file_name: Optional file name (uses original if not provided)
        
    Returns:
        Dict with 'file_id', 'file_name', 'file_url' or None
    """
    service = get_drive_service(indicator.project)
    if not service:
        return None
    
    # Determine file name
    if not file_name:
        if hasattr(file_obj, 'name'):
            file_name = os.path.basename(file_obj.name)
        else:
            file_name = 'uploaded_file'
    
    try:
        # Prepare file metadata
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        # Upload file
        if hasattr(file_obj, 'read'):
            # File object
            media = MediaIoBaseUpload(file_obj, mimetype='application/octet-stream', resumable=True)
        else:
            # File path
            media = MediaFileUpload(file_obj, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        file_name = file.get('name')
        file_url = file.get('webViewLink')
        
        # Make file viewable (not editable) by anyone with link
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()
        
        return {
            'file_id': file_id,
            'file_name': file_name,
            'file_url': file_url
        }
    except HttpError as e:
        print(f"Error uploading file to Drive: {e}")
        return None


def get_file_share_link(file_id: str, project: Project) -> Optional[str]:
    """
    Get or create sharing link for a file.
    
    Args:
        file_id: Google Drive file ID
        project: Project instance
        
    Returns:
        Sharing URL or None
    """
    service = get_drive_service(project)
    if not service:
        return None
    
    try:
        file = service.files().get(
            fileId=file_id,
            fields='webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    except HttpError as e:
        print(f"Error getting file share link: {e}")
        return None


def refresh_oauth_token(project: Project) -> bool:
    """
    Refresh OAuth token for a project.
    
    Args:
        project: Project instance
        
    Returns:
        True if refreshed, False otherwise
    """
    if not project.google_drive_oauth_token:
        return False
    
    try:
        creds = Credentials.from_authorized_user_info(
            json.loads(project.google_drive_oauth_token) if isinstance(project.google_drive_oauth_token, str)
            else project.google_drive_oauth_token
        )
        
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            project.google_drive_oauth_token = json.loads(creds.to_json())
            project.save(update_fields=['google_drive_oauth_token'])
            return True
    except Exception as e:
        print(f"Error refreshing token: {e}")
        return False
    
    return False


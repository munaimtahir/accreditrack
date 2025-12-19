import React, { useState, useEffect } from 'react';
import { getDriveAccessToken } from '../lib/googleAuth';
import { pickFolder } from '../lib/drivePicker';
import { projectService } from '../services/api';

interface Project {
  id: number;
  name: string;
  drive_folder_id?: string | null;
  evidence_storage_mode: 'local' | 'gdrive';
  drive_linked_at?: string | null;
  drive_linked_email?: string | null;
}

interface Props {
  project: Project;
  onLinked?: () => void;
}

const DriveFolderLinker: React.FC<Props> = ({ project, onLinked }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isIPAccess, setIsIPAccess] = useState(false);

  useEffect(() => {
    // Check if accessing via IP
    const hostname = window.location.hostname;
    const isIP = /^\d+\.\d+\.\d+\.\d+$/.test(hostname);
    setIsIPAccess(isIP);
  }, []);

  const handleLinkFolder = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get access token
      const accessToken = await getDriveAccessToken();

      // Pick folder
      const folderResult = await pickFolder(accessToken);

      // Get user email if available (from token info)
      // Note: We can't easily get email from token without decoding JWT
      // For now, we'll just send the folder ID

      // Link folder to project
      await projectService.linkDriveFolder(project.id, {
        drive_folder_id: folderResult.folderId,
        drive_linked_email: undefined, // Can be enhanced to get from token
      });

      if (onLinked) {
        onLinked();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to link Drive folder');
      console.error('Error linking Drive folder:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUnlinkFolder = async () => {
    if (!confirm('Are you sure you want to unlink this Drive folder? Evidence will switch to local storage.')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await projectService.unlinkDriveFolder(project.id);
      if (onLinked) {
        onLinked();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to unlink Drive folder');
      console.error('Error unlinking Drive folder:', err);
    } finally {
      setLoading(false);
    }
  };

  const isLinked = project.evidence_storage_mode === 'gdrive' && project.drive_folder_id;

  return (
    <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', marginBottom: '20px' }}>
      <h3 style={{ marginTop: 0 }}>Google Drive Integration</h3>

      {isIPAccess && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#fff3cd', 
          border: '1px solid #ffc107', 
          borderRadius: '4px',
          marginBottom: '15px'
        }}>
          <strong>Note:</strong> Drive linking requires accessing the app via{' '}
          <code>accredify.pmc.edu.pk</code>. Google OAuth may not work when accessing via IP address.
        </div>
      )}

      {error && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#f8d7da', 
          border: '1px solid #f5c6cb', 
          borderRadius: '4px',
          marginBottom: '15px',
          color: '#721c24'
        }}>
          {error}
        </div>
      )}

      {isLinked ? (
        <div>
          <p style={{ color: '#28a745', marginBottom: '10px' }}>
            ✓ Drive folder linked
            {project.drive_linked_at && (
              <span style={{ fontSize: '0.9em', color: '#666', marginLeft: '10px' }}>
                (Linked {new Date(project.drive_linked_at).toLocaleDateString()})
              </span>
            )}
          </p>
          <button
            onClick={handleUnlinkFolder}
            disabled={loading}
            style={{
              padding: '8px 16px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'Unlinking...' : 'Unlink Drive Folder'}
          </button>
        </div>
      ) : (
        <div>
          <p style={{ marginBottom: '10px' }}>
            No Drive folder linked. Evidence will be stored locally.
          </p>
          <button
            onClick={handleLinkFolder}
            disabled={loading}
            style={{
              padding: '8px 16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'Linking...' : 'Link Google Drive Folder'}
          </button>
        </div>
      )}
    </div>
  );
};

export default DriveFolderLinker;


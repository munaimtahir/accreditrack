/**
 * Google Drive API Operations
 * Handles file uploads and folder management
 */

const DRIVE_API_BASE = 'https://www.googleapis.com/drive/v3';
const DRIVE_UPLOAD_BASE = 'https://www.googleapis.com/upload/drive/v3';

export interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
  webViewLink: string;
}

/**
 * Check if a folder exists in a parent folder
 */
const findFolder = async (
  accessToken: string,
  parentId: string,
  folderName: string
): Promise<string | null> => {
  // Properly escape folder name for Drive API query
  // First escape backslashes, then escape single quotes
  const escapedFolderName = folderName.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
  const query = `name='${escapedFolderName}' and '${parentId}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false`;
  
  const response = await fetch(
    `${DRIVE_API_BASE}/files?q=${encodeURIComponent(query)}&fields=files(id)`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to search for folder: ${response.statusText}`);
  }

  const data = await response.json();
  return data.files && data.files.length > 0 ? data.files[0].id : null;
};

/**
 * Create a folder in Drive
 */
const createFolder = async (
  accessToken: string,
  parentId: string,
  folderName: string
): Promise<string> => {
  const metadata = {
    name: folderName,
    mimeType: 'application/vnd.google-apps.folder',
    parents: [parentId],
  };

  const response = await fetch(`${DRIVE_API_BASE}/files`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(metadata),
  });

  if (!response.ok) {
    throw new Error(`Failed to create folder: ${response.statusText}`);
  }

  const data = await response.json();
  return data.id;
};

/**
 * Ensure folder path exists, creating folders as needed
 * @param accessToken OAuth access token
 * @param rootFolderId Root folder ID (project folder)
 * @param sectionName Section name
 * @param standardName Standard name
 * @returns ID of the final folder (standard folder)
 */
export const ensureFolderPath = async (
  accessToken: string,
  rootFolderId: string,
  sectionName: string,
  standardName: string
): Promise<string> => {
  // Find or create section folder
  let sectionFolderId = await findFolder(accessToken, rootFolderId, sectionName);
  if (!sectionFolderId) {
    sectionFolderId = await createFolder(accessToken, rootFolderId, sectionName);
  }

  // Find or create standard folder within section folder
  let standardFolderId = await findFolder(accessToken, sectionFolderId, standardName);
  if (!standardFolderId) {
    standardFolderId = await createFolder(accessToken, sectionFolderId, standardName);
  }

  return standardFolderId;
};

/**
 * Upload a file to a specific folder in Drive
 * @param accessToken OAuth access token
 * @param folderId Target folder ID
 * @param file File to upload
 * @param filename Filename to use
 * @returns Drive file metadata
 */
export const uploadFileToFolder = async (
  accessToken: string,
  folderId: string,
  file: File,
  filename: string
): Promise<DriveFile> => {
  // Create metadata
  const metadata = {
    name: filename,
    parents: [folderId],
  };

  // Create multipart request body
  const boundary = '-------314159265358979323846';
  const delimiter = `\r\n--${boundary}\r\n`;
  const closeDelimiter = `\r\n--${boundary}--`;

  const metadataPart = delimiter + 'Content-Type: application/json\r\n\r\n' + JSON.stringify(metadata);

  const reader = new FileReader();
  
  return new Promise((resolve, reject) => {
    reader.onload = async () => {
      try {
        const fileContent = reader.result as ArrayBuffer;
        
        const body = new Blob([
          metadataPart,
          delimiter,
          'Content-Type: ',
          file.type || 'application/octet-stream',
          '\r\n\r\n',
          fileContent,
          closeDelimiter,
        ]);

        const response = await fetch(`${DRIVE_UPLOAD_BASE}/files?uploadType=multipart&fields=id,name,mimeType,webViewLink`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': `multipart/related; boundary=${boundary}`,
          },
          body,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(`Failed to upload file: ${errorData.error?.message || response.statusText}`);
        }

        const data = await response.json();
        resolve({
          id: data.id,
          name: data.name,
          mimeType: data.mimeType,
          webViewLink: data.webViewLink,
        });
      } catch (error) {
        reject(error);
      }
    };

    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };

    reader.readAsArrayBuffer(file);
  });
};

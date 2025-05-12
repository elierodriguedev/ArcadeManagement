import React, { useState } from 'react';

interface AgentUpdateProps {
    onUpdateSuccess?: () => void;
    updateStatus: 'idle' | 'checking' | 'found' | 'not found' | 'updating' | 'error'; // Add updateStatus prop
    onCheckForUpdate: () => void; // Add onCheckForUpdate prop
}

const AgentUpdate: React.FC<AgentUpdateProps> = ({ onUpdateSuccess, updateStatus, onCheckForUpdate }) => {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setError(null);
        setSuccess(null);
        setProgress(0);
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
        } else {
            setFile(null);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError('Please select an agent.exe file to upload.');
            return;
        }
        setUploading(true);
        setError(null);
        setSuccess(null);
        setProgress(0);
        try {
            // Calculate SHA256
            const arrayBuffer = await file.arrayBuffer();
            const hashBuffer = await window.crypto.subtle.digest('SHA-256', arrayBuffer);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const sha256 = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

            const formData = new FormData();
            formData.append('file', file);
            formData.append('sha256', sha256);

            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/update-agent', true);

            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                    setProgress(Math.round((event.loaded / event.total) * 100));
                }
            };

            xhr.onload = () => {
                setUploading(false);
                if (xhr.status === 200) {
                    setSuccess('Upload successful! Agent will restart shortly.');
                    setFile(null);
                    setProgress(0);
                    if (onUpdateSuccess) onUpdateSuccess();
                } else {
                    setError(`Upload failed: ${xhr.status} ${xhr.statusText} - ${xhr.responseText}`);
                }
            };

            xhr.onerror = () => {
                setUploading(false);
                setError('Upload failed due to a network error.');
            };

            xhr.send(formData);
        } catch (err) {
            setUploading(false);
            setError('Failed to compute SHA256 or upload: ' + (err instanceof Error ? err.message : String(err)));
        }
    };

    return (
      // Style the main container
      <div className="p-4 border rounded bg-white shadow-sm">
        {/* Style the heading */}
        <h4 className="text-lg font-semibold mb-3 text-gray-700">Update Agent</h4>
        {/* Style the status paragraph */}
        <p className="mb-3 text-sm text-gray-700">Current Status: {updateStatus}</p> {/* Display update status */}
        {/* Style the file input container */}
        <div className="mb-3">
          <input
            type="file"
            accept=".exe"
            onChange={handleFileChange}
            disabled={uploading}
            // Basic styling for file input
            className="text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>
        {/* Style the upload button */}
        <button
          onClick={handleUpload}
          disabled={uploading || !file}
          // Removed inline style, added Tailwind margin
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed ml-2"
        >
          {uploading ? `Uploading... (${progress}%)` : 'Upload Agent.exe'}
        </button>
        {/* Style the progress bar container and progress bar */}
        {progress > 0 && uploading && (
          <div className="mt-3">
            <progress value={progress} max={100} className="w-full h-2 rounded overflow-hidden appearance-none [&::-webkit-progress-bar]:bg-gray-200 [&::-webkit-progress-value]:bg-blue-500 [&::-moz-progress-bar]:bg-blue-500" />
          </div>
        )}
        {/* Style the error message */}
        {error && <div className="text-red-500 mt-2 text-sm">{error}</div>}
        {/* Style the success message */}
        {success && <div className="text-green-500 mt-2 text-sm">{success}</div>}
        {/* Style the check for update button container */}
        <div className="mt-4 pt-4 border-t">
          {/* Style the check for update button */}
          <button
            onClick={onCheckForUpdate}
            disabled={updateStatus === 'checking' || uploading}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {updateStatus === 'checking' ? 'Checking for Update...' : 'Check for Update'}
          </button>
        </div>
      </div>
    );
  };

export default AgentUpdate;

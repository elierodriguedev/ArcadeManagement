import React from 'react';
import { Tabs, Tab } from './Tabs';
import SystemStatus from './SystemStatus';
import LogViewer from './LogViewer';
import ScreenshotViewer from './ScreenshotViewer';
import ImageGenerator from './ImageGenerator';
import AgentUpdate from './AgentUpdate';
import ModeToggle from './ModeToggle'; // Import ModeToggle

interface ServerTabProps {
  logs: string[];
  logConnectionStatus: boolean;
  updateStatus: 'idle' | 'checking' | 'found' | 'not found' | 'updating' | 'error';
  currentMode: 'Arcade' | 'Pinball'; // Add currentMode prop
  onModeToggle: (mode: 'Arcade' | 'Pinball') => void; // Add onModeToggle prop
  onCheckForUpdate: () => void; // Add onCheckForUpdate prop
}

const ServerTab: React.FC<ServerTabProps> = ({ logs, logConnectionStatus, updateStatus, currentMode, onModeToggle, onCheckForUpdate }) => {
  return (
    // Add padding to the container
    <div className="p-4">
      {/* Style the heading */}
      <h2 className="text-xl font-bold mb-4 text-gray-700">Server Management</h2>
      <Tabs>
        <Tab label="Status">
          <ModeToggle currentMode={currentMode} onToggle={onModeToggle} /> {/* Include ModeToggle */}
          <SystemStatus /> {/* Pass mode props */}
        </Tab>
        <Tab label="Log">
          <LogViewer logs={logs} isConnected={logConnectionStatus} />
        </Tab>
        <Tab label="Screenshot">
          <ScreenshotViewer />
        </Tab>
        <Tab label="Image Generation">
          <ImageGenerator />
        </Tab>
        <Tab label="Check for Update">
          <AgentUpdate updateStatus={updateStatus} onCheckForUpdate={onCheckForUpdate} /> {/* Pass updateStatus and onCheckForUpdate */}
        </Tab>
      </Tabs>
    </div>
  );
};

export default ServerTab;
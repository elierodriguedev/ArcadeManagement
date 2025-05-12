import { useState, useEffect, useRef } from 'react'; // Added useRef
// import './App.css'; // Removed as we are using Tailwind

import { Tabs, Tab } from './components/Tabs'; // Import Tabs and Tab components
import ServerTab from './components/ServerTab'; // Import ServerTab
import ArcadeTab from './components/ArcadeTab'; // Import ArcadeTab

const MAX_LOG_LINES = 200; // Limit number of log lines stored

function App() {
  const [hostname, setHostname] = useState<string>('Loading...');
  const [agentVersion, setAgentVersion] = useState<string>('Loading...');

  // State for logs managed globally in App
  const [logs, setLogs] = useState<string[]>(['Initializing log stream...']);
  const [logConnectionStatus, setLogConnectionStatus] = useState<boolean>(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const [updateStatus, setUpdateStatus] = useState<'idle' | 'checking' | 'found' | 'not found' | 'updating' | 'error'>('idle');

  // State for current mode (Arcade or Pinball)
  const [currentMode, setCurrentMode] = useState<'Arcade' | 'Pinball'>('Arcade');

  // @ts-ignore: isUpdating is declared but its value is never read.
  const isUpdating = updateStatus === 'updating'; // Keep as it might be used later

  const handleCheckForUpdate = async () => {
    setUpdateStatus('checking');
    const agentPort = 5151; // Define agent port
    const baseUrl = `http://${window.location.hostname}:${agentPort}`;

    try {
      const response = await fetch(`${baseUrl}/api/check_update`);
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      const data = await response.json();
      if (data.update_available) {
        setUpdateStatus('found');
        // Optionally trigger the update process here or show a confirmation
        // For now, let's just log and indicate that an update is found
        console.log("Update found:", data.latest_version);
      } else {
        setUpdateStatus('not found');
      }
    } catch (error) {
      console.error("Error checking for update:", error);
      setUpdateStatus('error');
    }
  };

  // Handler for mode toggle
  const handleModeToggle = (mode: 'Arcade' | 'Pinball') => {
    setCurrentMode(mode);
  };


  useEffect(() => {
    const agentPort = 5151; // Define agent port
    const baseUrl = `http://${window.location.hostname}:${agentPort}`;

    fetch(`${baseUrl}/api/ping`)
      .then(res => res.ok ? res.json() : Promise.reject(`HTTP error ${res.status}`))
      .then(data => {
        setHostname(data.hostname || 'N/A');
        setAgentVersion(data.version || 'N/A');
      })
      .catch(error => {
        console.error("Error fetching initial ping data:", error);
        setHostname('Error');
        setAgentVersion('Error');
      });
  }, []);

  useEffect(() => {
    const agentPort = 5151; // Define agent port
    const baseUrl = `http://${window.location.hostname}:${agentPort}`;

    const connectLogStream = () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }
        const es = new EventSource(`${baseUrl}/log`);
        eventSourceRef.current = es;
        setLogConnectionStatus(false);
        setLogs(['Connecting to log stream...']);
        es.onopen = () => {
            setLogs(prev => [...prev.slice(-MAX_LOG_LINES), '--- Connection opened ---']);
            setLogConnectionStatus(true);
        };
        es.onmessage = (event) => {
            setLogs(prev => {
                const newLogs = [...prev.slice(-MAX_LOG_LINES), event.data];
                return newLogs;
            });
        };
        es.onerror = () => {
            setLogs(prev => [...prev.slice(-MAX_LOG_LINES), '--- Log stream connection error or closed ---']);
            setLogConnectionStatus(false);
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
            }
        };
    };
    connectLogStream();
    return () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
    };
  }, []);

  return (
    // Apply Tailwind classes for overall page layout and background
    <div className="bg-gray-100 min-h-screen font-sans p-5">
      {/* Apply container, background, padding, rounded corners, and shadow like the controller */}
      <div className="container mx-auto bg-white p-5 rounded-lg shadow-md">
        <header className="text-center mb-6">
          {/* Style H1 like the controller */}
          <h1 className="text-2xl font-bold text-gray-800">Arcade Agent UI</h1>
          {/* Style the info div */}
          <div className="text-sm text-gray-600 mt-1">Host: {hostname} | Agent Version: {agentVersion}</div>
        </header>
        <main>
          <Tabs>
            <Tab label="Server">
              <ServerTab
              logs={logs}
              logConnectionStatus={logConnectionStatus}
              updateStatus={updateStatus}
              currentMode={currentMode} // Pass currentMode
              onModeToggle={handleModeToggle} // Pass mode toggle handler
              onCheckForUpdate={handleCheckForUpdate} // Pass handleCheckForUpdate
            />
          </Tab>
          <Tab label="Arcade">
            <ArcadeTab />
          </Tab>
          <Tab label="Pinball">
            {/* Pinball Tab Content - Placeholder */}
            <div>Pinball Tab Content</div>
          </Tab>
        </Tabs>
        </main>
      </div> {/* Close container div */}
    </div>
  );
}

export default App;

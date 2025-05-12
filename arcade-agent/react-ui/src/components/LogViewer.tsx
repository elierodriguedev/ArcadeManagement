import React, { useEffect, useRef } from 'react';

// Define props interface
interface LogViewerProps {
    logs: string[];
    isConnected: boolean;
}

const LogViewer: React.FC<LogViewerProps> = ({ logs, isConnected }) => {
    // Remove internal state for logs and connection status
    // const [logs, setLogs] = useState<string[]>(['Connecting to log stream...']);
    // const [isConnected, setIsConnected] = useState<boolean>(false);
    // const eventSourceRef = useRef<EventSource | null>(null);

    const logOutputRef = useRef<HTMLPreElement>(null); // Ref for scrolling

    // Remove the useEffect that managed the EventSource connection - App.tsx handles this now
    /*
    useEffect(() => {
        // ... connection logic removed ...
    }, []);
    */

    // Effect to scroll to bottom when logs prop updates
    useEffect(() => {
        if (logOutputRef.current) {
            logOutputRef.current.scrollTop = logOutputRef.current.scrollHeight;
        }
    }, [logs]); // Run whenever logs prop changes

    return (
      // Style the main container
      <div className="p-4 border rounded bg-white shadow-sm">
        {/* Style the heading */}
        <h3 className="text-lg font-semibold mb-3 text-gray-700">Agent Log</h3>
        {/* Style the status paragraph and text */}
        <p className="mb-2 text-sm">
          Status: <span className={`font-medium ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </p>
        {/* Style the log output area */}
        <pre
          ref={logOutputRef}
          id="log-output"
          className="bg-gray-900 text-gray-200 p-4 rounded font-mono text-sm h-80 overflow-y-auto whitespace-pre-wrap"
        >
          {/* Display logs based on prop */}
          {logs.map((entry, i) => (
            // Use a div instead of span for block display of each log entry
            <div key={i} dangerouslySetInnerHTML={{ __html: entry.replace(/\\n|\n/g, '<br/>') }} />
                ))}
            </pre>
        </div>
    );
};

export default LogViewer;

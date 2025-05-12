import React, { useState, useEffect, useCallback } from 'react'; // Added imports

interface PingData { // Added PingData interface
    status: string;
    type: string;
    hostname: string;
    version: string;
    disk_total_gb: number | string;
    disk_free_gb: number | string;
    cpu_percent: number | string;
    ram_percent: number | string;
    bigbox_running: boolean;
}

const ArcadeControlsTab: React.FC = () => {
    const [statusData, setStatusData] = useState<PingData | null>(null); // Added state
    const [loading, setLoading] = useState<boolean>(true); // Added state
    const [error, setError] = useState<string | null>(null); // Added state
    const [buttonLoading, setButtonLoading] = useState<'start' | 'stop' | 'deleteCache' | null>(null); // Added state

    const fetchStatus = useCallback(async () => { // Added fetchStatus function
        setError(null);
        try {
            const response = await fetch('/api/ping');
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            const data: PingData = await response.json();
            setStatusData(data);
        } catch (err) {
            console.error("Error fetching system status:", err);
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
            setStatusData(null);
        } finally {
            setLoading(false);
        }
    }, []);

    const handleDeleteCache = useCallback(async () => { // Added handleDeleteCache function
        setButtonLoading('deleteCache');
        setError(null);
        try {
            const response = await fetch('/api/launchbox/delete_cache', { method: 'POST' });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`HTTP error ${response.status}: ${errorData.error || 'Failed to delete cache'}`);
            }
            console.log("Delete cache request successful");
            setTimeout(() => fetchStatus(), 1500);
        } catch (err) {
            console.error("Error deleting cache:", err);
            setError(`Delete cache failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
        } finally {
            setButtonLoading(null);
        }
    }, [fetchStatus]);

    useEffect(() => { // Added useEffect hook
        fetchStatus();
        const intervalId = setInterval(fetchStatus, 5000);
        return () => clearInterval(intervalId);
    }, [fetchStatus]);

    const handleStartBigBox = async () => { // Added handleStartBigBox function
        setButtonLoading('start');
        setError(null);
        try {
            const response = await fetch('/api/launchbox/start_bigbox', { method: 'POST' });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`HTTP error ${response.status}: ${errorData.error || 'Failed to start'}`);
            }
            console.log("Start BigBox request successful");
            setTimeout(fetchStatus, 1500);
        } catch (err) {
            console.error("Error starting BigBox:", err);
            setError(`Start failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
        } finally {
            setButtonLoading(null);
        }
    };

    const handleStopBigBox = async () => { // Added handleStopBigBox function
        setButtonLoading('stop');
        setError(null);
        try {
            const response = await fetch('/api/launchbox/stop_bigbox', { method: 'POST' });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`HTTP error ${response.status}: ${errorData.error || 'Failed to stop'}`);
            }
            console.log("Stop BigBox request successful");
            setTimeout(fetchStatus, 1500);
        } catch (err) {
            console.error("Error stopping BigBox:", err);
            setError(`Stop failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
        } finally {
            setButtonLoading(null);
        }
    };

    if (loading && !statusData) { // Added loading state
        // Style loading message
        return <div className="text-gray-600 p-4">Loading arcade controls status...</div>;
    }

    if (error && !statusData) { // Added error state
         // Style error message
         return <div className="text-red-500 p-4">Error loading arcade controls status: {error}</div>;
    }

    // Style polling warning
    const pollingError = error && statusData ? <p className="text-orange-500 mt-2 text-sm">Warning: Could not refresh status ({error}). Displaying last known data.</p> : null; // Added polling error

    return (
        // Style the main container
        <div className="p-4 border rounded bg-white shadow-sm">
            {/* Style the heading */}
            <h3 className="text-lg font-semibold mb-3 text-gray-700">Arcade Controls</h3>
            {pollingError} {/* Display polling error */}
            {statusData ? ( // Added status data check
                <>
                    {/* Style BigBox status display */}
                    <p className="mb-4 text-sm text-gray-700">
                        <strong>BigBox Status:</strong>
                        <span id="bigbox-status" className={`ml-1 font-medium ${statusData.bigbox_running ? 'text-green-600' : 'text-red-600'}`}>
                            {statusData.bigbox_running ? '✔ Running' : '✘ Not Running'}
                        </span>
                    </p>

                    {/* Style control buttons section */}
                    <div className="control-section mt-4 pt-4 border-t border-gray-200">
                        {/* Style control section heading */}
                        <h4 className="text-lg font-semibold mb-3 text-gray-700">Control</h4>
                        {!statusData.bigbox_running && (
                            <button
                                id="start-bigbox-button"
                                onClick={handleStartBigBox}
                                disabled={buttonLoading === 'start'}
                                // Style Start BigBox button
                                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed mr-2"
                            >
                                {buttonLoading === 'start' ? 'Starting...' : 'Start BigBox'}
                            </button>
                        )}
                        {statusData.bigbox_running && (
                            <button
                                id="stop-bigbox-button"
                                onClick={handleStopBigBox}
                                disabled={buttonLoading === 'stop'}
                                // Style Stop BigBox button
                                className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed mr-2"
                            >
                                {buttonLoading === 'stop' ? 'Stopping...' : 'Stop BigBox'}
                            </button>
                        )}
                        {/* Style Delete Cache button container */}
                        <div className="mt-3">
                            <button
                                id="delete-cache-button"
                                onClick={handleDeleteCache}
                                disabled={buttonLoading === 'deleteCache'}
                                // Style Delete Cache button
                                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {buttonLoading === 'deleteCache' ? 'Deleting Cache...' : 'Delete Cache'}
                            </button>
                        </div>
                    </div>
                </>
            ) : (
                // Style unavailable status message
                <p className="text-gray-600">Arcade control status data unavailable.</p>
            )}
        </div>
    );
};

export default ArcadeControlsTab;
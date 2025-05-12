import React, { useState, useEffect, useCallback } from 'react';

interface SystemStatusProps {
    // updateStatus is not used in SystemStatus
}

interface PingData {
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

const SystemStatus: React.FC<SystemStatusProps> = ({ }) => {
    const [statusData, setStatusData] = useState<PingData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [rebooting, setRebooting] = useState<boolean>(false);
    const [rebootError, setRebootError] = useState<string | null>(null);
    const [reconnectAttempts, setReconnectAttempts] = useState<number>(0);
    const MAX_RECONNECT_ATTEMPTS = 10; // Define max reconnection attempts
    const RECONNECT_DELAY_MS = 5000; // Initial delay before first reconnection attempt

    const fetchStatus = useCallback(async () => {
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

    useEffect(() => {
        fetchStatus();
        const intervalId = setInterval(fetchStatus, 5000);
        return () => clearInterval(intervalId);
    }, [fetchStatus]);

    const handleReboot = async () => {
        setRebooting(true);
        setRebootError(null);
        setReconnectAttempts(0); // Reset reconnection attempts

        try {
            // Replace 'your_secret_token' with the actual token or a more secure method
            const response = await fetch('/api/reboot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Agent-Auth': 'your_secret_token' // Use the same token as in api_routes.py
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error ${response.status}: ${errorData.error || response.statusText}`);
            }

            // Assuming the API returns a success status immediately
            // Start reconnection attempts after a delay
            setTimeout(attemptReconnect, RECONNECT_DELAY_MS);

        } catch (err) {
            console.error("Error initiating reboot:", err);
            setRebootError(err instanceof Error ? err.message : 'An unknown error occurred');
            setRebooting(false); // Re-enable button on immediate error
        }
    };

    const attemptReconnect = useCallback(async () => {
        if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            setRebootError("Agent appears to be offline.");
            setRebooting(false); // Stop trying to reconnect
            return;
        }

        setReconnectAttempts(prev => prev + 1);
        console.log(`Attempting to reconnect, attempt ${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS}`);

        try {
            const response = await fetch('/api/ping');
            if (response.ok) {
                // Successfully reconnected
                console.log("Successfully reconnected to agent.");
                fetchStatus(); // Fetch latest status
                setRebooting(false); // Hide rebooting indicator
                setRebootError(null); // Clear any previous reboot errors
                setReconnectAttempts(0); // Reset attempts
            } else {
                // Agent not yet available, retry after increasing delay
                const delay = RECONNECT_DELAY_MS * Math.pow(2, reconnectAttempts); // Exponential backoff
                console.log(`Reconnect failed, retrying in ${delay}ms`);
                setTimeout(attemptReconnect, delay);
            }
        } catch (err) {
            // Network error or agent not responding, retry after increasing delay
            const delay = RECONNECT_DELAY_MS * Math.pow(2, reconnectAttempts); // Exponential backoff
            console.error(`Reconnect attempt failed: ${err}. Retrying in ${delay}ms`);
            setTimeout(attemptReconnect, delay);
        }
    }, [reconnectAttempts, fetchStatus]); // Added fetchStatus to dependencies

    const renderDiskUsage = () => {
        if (!statusData || statusData.disk_total_gb === 'N/A' || statusData.disk_free_gb === 'N/A') {
            return (
                <>
                    {/* Style progress label */}
                    <label className="block text-sm font-medium text-gray-600 mb-1" id="disk-label">Disk Space: N/A</label>
                    {/* Basic progress bar styling (appearance might vary by browser) */}
                    <progress id="disk-space" value="0" max="100" className="w-full h-2 rounded overflow-hidden appearance-none [&::-webkit-progress-bar]:bg-gray-200 [&::-webkit-progress-value]:bg-blue-500 [&::-moz-progress-bar]:bg-blue-500"></progress>
                </>
            );
        }
        const total = Number(statusData.disk_total_gb);
        const free = Number(statusData.disk_free_gb);
        const used = total - free;
        const usedPercent = total > 0 ? (used / total) * 100 : 0;

        return (
            <>
                {/* Style progress label */}
                <label className="block text-sm font-medium text-gray-600 mb-1" id="disk-label">
                    Disk Space (Free: {free.toFixed(1)} GB / {total.toFixed(1)} GB)
                </label>
                {/* Basic progress bar styling */}
                <progress id="disk-space" value={used.toFixed(1)} max={total.toFixed(1)} title={`${usedPercent.toFixed(1)}% used`} className="w-full h-2 rounded overflow-hidden appearance-none [&::-webkit-progress-bar]:bg-gray-200 [&::-webkit-progress-value]:bg-blue-500 [&::-moz-progress-bar]:bg-blue-500"></progress>
            </>
        );
    };

    if (loading && !statusData) {
        // Style loading message
        return <div className="text-gray-600">Loading system status...</div>;
    }

    if (error && !statusData) {
         // Style error message
         return <div className="text-red-500">Error loading system status: {error}</div>;
    }

    // Style polling warning
    const pollingError = error && statusData ? <p className="text-orange-500 mt-2 text-sm">Warning: Could not refresh status ({error}). Displaying last known data.</p> : null;

    return (
        // Add padding to main container
        <div className="p-4 border rounded bg-white shadow-sm">
            {/* Style heading */}
            <h3 className="text-lg font-semibold mb-3 text-gray-700">System Status</h3>
            {pollingError}
            {/* Use grid for layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {statusData ? (
                    <>
                        {/* Info Section */}
                        <div className="space-y-2">
                            {/* Style info lines */}
                            <div>
                                <span className="font-medium text-gray-600 mr-2">CPU Usage:</span>
                                <span className="text-gray-800">{statusData.cpu_percent}%</span>
                            </div>
                            <div>
                                <span className="font-medium text-gray-600 mr-2">RAM Usage:</span>
                                <span className="text-gray-800">{statusData.ram_percent}%</span>
                            </div>
                            {/* Style progress container */}
                            <div className="mt-2">
                                {renderDiskUsage()}
                            </div>
                        </div>
                    </>
                ) : (
                    <p className="text-gray-600">Status data unavailable.</p>
                )}
            </div>

            {/* Reboot Button Section */}
            <div className="mt-5 pt-4 border-t">
                <button
                    onClick={handleReboot}
                    disabled={rebooting}
                    // Style reboot button
                    className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {rebooting ? 'Rebooting...' : 'Reboot Agent'}
                </button>
                {/* Style reboot status/error messages */}
                {rebootError && <p className="text-red-500 mt-2 text-sm">Reboot failed: {rebootError}</p>}
                {rebooting && !rebootError && <p className="text-orange-500 mt-2 text-sm">Attempting to reconnect...</p>}
            </div>
        </div>
    );
};

export default SystemStatus;

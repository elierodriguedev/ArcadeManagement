import { useState, useEffect } from 'react'; // Import useState and useEffect

function ScreenshotViewer() {
  const [screenshotUrl, setScreenshotUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const fetchScreenshot = async () => {
    setError(null);
    try {
      const response = await fetch('/api/screenshot');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      // Load image in memory first to prevent flickering
      const img = new Image();
      img.onload = () => {
        // Revoke the previous object URL to free up memory
        if (screenshotUrl) {
          URL.revokeObjectURL(screenshotUrl);
        }
        setScreenshotUrl(url);
        setLastUpdated(new Date().toLocaleString());
      };
      img.onerror = () => {
        setError('Failed to load new screenshot image.');
        URL.revokeObjectURL(url); // Clean up the new object URL
      };
      img.src = url;

    } catch (e: any) {
      console.error("Error fetching screenshot:", e);
      setError(`Failed to load screenshot: ${e.message}`);
    }
  };

  useEffect(() => {
    // Fetch screenshot initially
    fetchScreenshot();

    // Set up interval to fetch screenshot every 2 seconds
    const intervalId = setInterval(fetchScreenshot, 2000);

    // Clean up interval on component unmount
    return () => {
      clearInterval(intervalId);
      // Revoke the last object URL on unmount
      if (screenshotUrl) {
        URL.revokeObjectURL(screenshotUrl);
      }
    };
  }, [screenshotUrl]); // Add screenshotUrl to dependency array to revoke previous URL

  return (
    // Style the main container
    <div className="p-4 border rounded bg-white shadow-sm">
      {/* Style the heading */}
      <h2 className="text-lg font-semibold mb-3 text-gray-700">Live Screenshot</h2>
      {/* Style the error message */}
      {error && <p className="text-red-500 mb-2 text-sm">{error}</p>}
      {screenshotUrl ? (
        <>
          <img
            src={screenshotUrl}
            alt="Live Screenshot"
            // Style the image
            className="max-w-full h-auto border rounded shadow-sm"
          />
          {/* Style the last updated text */}
          {lastUpdated && <p className="text-xs text-gray-500 mt-1">Last updated: {lastUpdated}</p>}
        </>
      ) : (
        // Style the placeholder text
        !error && <p className="text-gray-500">Screenshot will appear here.</p>
      )}
    </div>
  );
}

export default ScreenshotViewer;

import { useState } from 'react'; // Import useState

function ImageGenerator() {
  const [prompt, setPrompt] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [size, setSize] = useState(''); // State for size input
  const [useOpenAI, setUseOpenAI] = useState(false); // State for OpenAI checkbox

  const handleGenerateImage = async () => {
    setLoading(true);
    setError('');
    setImageUrl('');

    try {
      const agentPort = 5151;
      const baseUrl = `http://${window.location.hostname}:${agentPort}`;
      let apiUrl = '';
      let finalPrompt = prompt;

      if (useOpenAI) {
        // Use the new endpoint for OpenAI
        apiUrl = `${baseUrl}/api/generate-image-gpt?prompt=${encodeURIComponent(prompt)}&size=${encodeURIComponent(size)}`;
      } else {
        // Use the existing endpoint and append size to prompt
        finalPrompt = `${prompt} Image size should be of ${size}`;
        apiUrl = `${baseUrl}/api/generate-image?prompt=${encodeURIComponent(finalPrompt)}`;
      }

      const response = await fetch(apiUrl, {
        method: 'GET',
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Error generating image: ${response.status} ${response.statusText} - ${errorData}`);
      }

      const imageBlob = await response.blob();

      const reader = new FileReader();
      reader.onloadend = () => {
        setImageUrl(reader.result as string);
      };
      reader.readAsDataURL(imageBlob);

    } catch (err: any) {
      setError(err.message);
      console.error("Error generating image:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    // Style the main container
    <div className="p-4 border rounded bg-white shadow-sm">
      {/* Style the heading */}
      <h2 className="text-lg font-semibold mb-3 text-gray-700">Image Generation</h2>
      {/* Style the textarea container and textarea */}
      <div className="mb-4">
        <textarea
          rows={4}
          // Removed cols as width is handled by Tailwind
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your image prompt here..."
          disabled={loading}
          // Style the textarea
          className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        />
      </div>
      {/* Style the size input container */}
      <div className="flex items-center mb-3">
        {/* Style the label */}
        <label htmlFor="size" className="mr-2 font-medium text-gray-700">Size:</label>
        {/* Style the input */}
        <input
          type="text"
          id="size"
          value={size}
          onChange={(e) => setSize(e.target.value)}
          disabled={loading}
          className="border rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus-ring-blue-500 disabled:opacity-50"
        />
      </div>
      {/* Style the OpenAI checkbox container */}
      <div className="flex items-center mb-4">
        {/* Style the label */}
        <label htmlFor="useOpenAI" className="mr-2 font-medium text-gray-700">Use OpenAI:</label>
        {/* Style the checkbox */}
        <input
          type="checkbox"
          id="useOpenAI"
          checked={useOpenAI}
          onChange={(e) => setUseOpenAI(e.target.checked)}
          disabled={loading}
          className="disabled:opacity-50"
        />
      </div>
      {/* Style the generate button */}
      <button
        onClick={handleGenerateImage}
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Generating...' : 'Generate Image'}
      </button>
      {/* Style the error message */}
      {error && <div className="text-red-500 mt-3 text-sm">Error: {error}</div>}
      {imageUrl && (
        // Style the result container
        <div className="mt-4 pt-4 border-t">
          {/* Style the result heading */}
          <h3 className="text-lg font-semibold mb-2 text-gray-700">Result:</h3>
          {/* Style the generated image */}
          <img src={imageUrl} alt="Generated Image" className="max-w-full h-auto border rounded shadow-sm" />
        </div>
      )}
    </div>
  );
}

export default ImageGenerator;

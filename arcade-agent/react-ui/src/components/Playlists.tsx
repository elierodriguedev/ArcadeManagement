import React, { useState, useEffect, useCallback } from 'react'; // Import useCallback

// Re-use Game interface if needed, or define specific types
interface Game {
    id: string;
    title: string;
    platform: string;
    path: string;
}

interface Playlist {
    name: string;
    gameIds: string[];
    game_count: number;
    bannerImagePath?: string; // Added optional banner image path
}

const Playlists: React.FC = () => {
    const [playlists, setPlaylists] = useState<Playlist[]>([]);
    const [loadingPlaylists, setLoadingPlaylists] = useState<boolean>(true);
    const [errorPlaylists, setErrorPlaylists] = useState<string | null>(null);

    const [selectedPlaylistName, setSelectedPlaylistName] = useState<string | null>(null);
    const [playlistGames, setPlaylistGames] = useState<Game[]>([]);
    const [loadingGames, setLoadingGames] = useState<boolean>(false);
    const [errorGames, setErrorGames] = useState<string | null>(null);

    // State for generated images (temporary URLs) and loading state
    const [generatedImageUrls, setGeneratedImageUrls] = useState<{ [playlistName: string]: string }>({});
    const [generatingImage, setGeneratingImage] = useState<{ [playlistName: string]: boolean }>({});


    // Fetch playlists
    const fetchPlaylists = useCallback(async () => {
        setLoadingPlaylists(true);
        setErrorPlaylists(null);
        try {
            const response = await fetch('/api/launchbox/playlists');
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            const data: Playlist[] = await response.json();
            setPlaylists(data);
        } catch (err) {
            console.error("Error fetching playlists:", err);
            setErrorPlaylists(err instanceof Error ? err.message : 'An unknown error occurred');
            setPlaylists([]);
        } finally {
            setLoadingPlaylists(false);
        }
    }, [setLoadingPlaylists, setErrorPlaylists, setPlaylists]); // Add dependencies

    // Fetch playlists on mount
    useEffect(() => {
        fetchPlaylists();
    }, [fetchPlaylists]); // Add fetchPlaylists as a dependency

    // Fetch games when a playlist is selected
    const handlePlaylistSelect = async (playlist: Playlist) => {
        if (selectedPlaylistName === playlist.name) {
             setSelectedPlaylistName(null); // Deselect if clicking the same one
             setPlaylistGames([]);
             return;
        }

        setSelectedPlaylistName(playlist.name);
        setPlaylistGames([]); // Clear previous games
        setErrorGames(null);

        if (!playlist.gameIds || playlist.gameIds.length === 0) {
            setLoadingGames(false);
            return; // No games to fetch
        }

        setLoadingGames(true);
        try {
            console.log("Fetching game details for playlist:", playlist.name, "IDs:", playlist.gameIds);
            const response = await fetch('/api/launchbox/games/details', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: playlist.gameIds }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`HTTP error ${response.status}: ${errorData.error || response.statusText}`);
            }
            const gamesData: Game[] = await response.json();
            setPlaylistGames(gamesData);
            console.log("Received games:", gamesData);
        } catch (err) {
            console.error("Error fetching playlist game details:", err);
            setErrorGames(err instanceof Error ? err.message : 'An unknown error occurred');
            setPlaylistGames([]);
        } finally {
            setLoadingGames(false);
        }
    };

    // Delete playlist
    const handleDeletePlaylist = async (playlistName: string, event: React.MouseEvent) => {
        event.stopPropagation(); // Prevent triggering playlist selection

        if (!window.confirm(`Are you sure you want to delete playlist "${playlistName}"?\nThis cannot be undone.`)) {
            return;
        }

        console.log(`Attempting to delete playlist: ${playlistName}`);
        try {
            const response = await fetch(`/api/launchbox/playlists/${encodeURIComponent(playlistName)}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                console.log(`Playlist "${playlistName}" deleted successfully.`);
                // Remove from state
                setPlaylists(prev => prev.filter(p => p.name !== playlistName));
                // Clear selection if the deleted one was selected
                if (selectedPlaylistName === playlistName) {
                    setSelectedPlaylistName(null);
                    setPlaylistGames([]);
                }
            } else {
                const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
                console.error(`Failed to delete playlist "${playlistName}":`, errorData);
                alert(`Error deleting playlist: ${errorData.error || response.statusText}`);
            }
        } catch (error) {
            console.error(`Network or other error deleting playlist "${playlistName}":`, error);
            alert(`Error deleting playlist: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    };

    const handleGenerateImage = async (playlist: Playlist) => {
        setGeneratingImage(prev => ({ ...prev, [playlist.name]: true }));
        setGeneratedImageUrls(prev => ({ ...prev, [playlist.name]: '' })); // Clear previous generated image URL

        const initialPrompt = `the last line is the text that should be displayed. 1049x280 Banner image for a game. It should have a transparent background and contrasting text . There should be an image to the left of the text that is related to it\n${playlist.name}`;
        const encodedInitialPrompt = encodeURIComponent(initialPrompt);

        try {
            // Step 1: Improve Prompt
            const improveResponse = await fetch(`/api/improve-prompt?prompt=${encodedInitialPrompt}`);
            if (!improveResponse.ok) {
                throw new Error(`HTTP error improving prompt: ${improveResponse.status}`);
            }
            const improveData = await improveResponse.json();
            const improvedPrompt = improveData.improved_prompt;
            console.log("Improved prompt:", improvedPrompt);

            // Step 2: Generate Image and get Temporary URL
            const encodedImprovedPrompt = encodeURIComponent(improvedPrompt);
            // Assuming the backend now returns a JSON object with a temp_image_url field
            const generateResponse = await fetch(`/api/generate-image?prompt=${encodedImprovedPrompt}`);
             if (!generateResponse.ok) {
                 throw new Error(`HTTP error generating image: ${generateResponse.status}`);
             }
            const generateData = await generateResponse.json();
            const tempImageUrl = generateData.temp_image_url; // Get the temporary URL from the response
            console.log("Generated temporary image URL:", tempImageUrl);

            // Step 3: Update state to display temporary image
            setGeneratedImageUrls(prev => ({ ...prev, [playlist.name]: tempImageUrl }));

        } catch (error) {
            console.error(`Error generating image for playlist ${playlist.name}:`, error);
            // Optionally display an error message next to the playlist item
        } finally {
            setGeneratingImage(prev => ({ ...prev, [playlist.name]: false }));
        }
    };

    const handleApplyImage = async (playlistName: string, tempImageUrl: string) => {
        console.log(`Attempting to apply image for playlist: ${playlistName} from URL: ${tempImageUrl}`);
        try {
            const response = await fetch('/api/launchbox/playlists/apply_banner', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ playlist_name: playlistName, temp_image_url: tempImageUrl }),
            });

            if (response.ok) {
                console.log(`Image applied successfully for playlist "${playlistName}".`);
                // Clear the temporary image URL from state
                setGeneratedImageUrls(prev => {
                    const newState = { ...prev };
                    delete newState[playlistName];
                    return newState;
                });
                // Reload the playlists to show the permanent image and hide the GenAI button
                fetchPlaylists();
            } else {
                const errorData = await response.json().catch(() => ({ error: `HTTP error ${response.status}` }));
                console.error(`Failed to apply image for playlist "${playlistName}":`, errorData);
                alert(`Error applying image: ${errorData.error || response.statusText}`);
            }
        } catch (error) {
            console.error(`Network or other error applying image for playlist "${playlistName}":`, error);
            alert(`Error applying image: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    };


    const getImageUrl = (game: Game): string => {
        const platformEncoded = encodeURIComponent(game.platform || '');
        const titleEncoded = encodeURIComponent(game.title || '');
        return `/img/${platformEncoded}/${titleEncoded}`;
    };

    return (
        // Style the main container
        <div className="p-4 border rounded bg-white shadow-sm">
            {/* Style the heading */}
            <h3 className="text-lg font-semibold mb-3 text-gray-700">Playlists</h3>
            {loadingPlaylists ? (
                // Style loading message
                <p className="text-gray-600">Loading playlists...</p>
            ) : errorPlaylists ? (
                // Style error message
                <p className="text-red-500">Error loading playlists: {errorPlaylists}</p>
            ) : playlists.length === 0 ? (
                // Style empty state message
                <p className="text-gray-600">No playlists found.</p>
            ) : (
                // Style the playlist list
                <ul id="playlist-list-ul" className="divide-y divide-gray-200">
                    {playlists.map((playlist) => (
                        <li
                            key={playlist.name}
                            onClick={() => handlePlaylistSelect(playlist)}
                            // Apply Tailwind classes for layout, padding, cursor, and conditional styles
                            className={`flex items-center justify-between py-2 px-3 cursor-pointer hover:bg-gray-100 ${
                                selectedPlaylistName === playlist.name ? 'bg-gray-200 font-semibold' : ''
                            }`}
                            title={`Click to view games in ${playlist.name}`}
                        >
                            {/* Container for image/button and text */}
                            <div className="flex items-center">
                                {/* Conditional rendering for image, apply button, GenAI button, or loading */}
                                {generatedImageUrls[playlist.name] ? (
                                    <> {/* Use a fragment to group the image and apply button */}
                                        <img
                                            src={generatedImageUrls[playlist.name]}
                                            alt={`${playlist.name} Generated Banner`}
                                            // Style the generated image
                                            className="max-w-[100px] max-h-[50px] mr-3 object-cover rounded" // Adjust size and add object-cover
                                            onError={(e) => {
                                                e.currentTarget.style.display = 'none';
                                                console.error(`Failed to load temporary generated image for ${playlist.name}`);
                                                // Optionally clear the temporary URL state if the image fails to load
                                                setGeneratedImageUrls(prev => {
                                                    const newState = { ...prev };
                                                    delete newState[playlist.name];
                                                    return newState;
                                                });
                                            }}
                                        />
                                        {/* Style the Apply button */}
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation(); // Prevent selecting playlist
                                                handleApplyImage(playlist.name, generatedImageUrls[playlist.name]);
                                            }}
                                            className="px-2 py-1 bg-green-500 text-white rounded text-xs hover:bg-green-600 focus:outline-none mr-3" // Add margin
                                        >
                                            Apply
                                        </button>
                                    </>
                                ) : playlist.bannerImagePath ? (
                                    <img
                                        // Use the new API endpoint to serve the image
                                        src={`/api/launchbox/playlists/banner/${encodeURIComponent(playlist.name)}`}
                                        alt={`${playlist.name} Banner`}
                                        // Style the banner image
                                        className="max-w-[100px] max-h-[50px] mr-3 object-cover rounded" // Adjust size and add object-cover
                                        onError={(e) => (e.currentTarget.style.display = 'none')} // Hide if image fails to load
                                    />
                                ) : generatingImage[playlist.name] ? (
                                    // Style the loading indicator
                                    <span className="text-gray-500 text-sm mr-3">Generating...</span> // Add margin and text style
                                ) : (
                                    // Style the GenAI button
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation(); // Prevent selecting playlist when clicking button
                                            handleGenerateImage(playlist);
                                        }}
                                        className="px-2 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600 focus:outline-none mr-3" // Add margin
                                    >
                                        GenAI
                                    </button>
                                )}
                                {/* Style the playlist name span */}
                                <span className="playlist-name text-gray-800">
                                    {playlist.name} ({playlist.game_count} games)
                                </span>
                            </div>
                            {/* Style the delete button */}
                            <button
                                className="delete-playlist-btn text-red-500 hover:text-red-700 focus:outline-none" // Apply text color and hover
                                onClick={(e) => handleDeletePlaylist(playlist.name, e)}
                                title={`Delete playlist ${playlist.name}`}
                            >
                                X
                            </button>
                        </li>
                    ))}
                </ul>
            )}

            {selectedPlaylistName && (
                // Style the selected playlist game display container
                <div id="playlist-game-display" className="mt-6 pt-4 border-t border-gray-200">
                    {/* Style the heading */}
                    <h4 className="text-lg font-semibold mb-3 text-gray-700">Games in "{selectedPlaylistName}"</h4>
                    {loadingGames ? (
                        // Style loading message
                        <p className="text-gray-600">Loading games...</p>
                    ) : errorGames ? (
                        // Style error message
                        <p className="text-red-500">Error loading games: {errorGames}</p>
                    ) : playlistGames.length === 0 ? (
                        // Style empty state message
                        <p className="text-gray-600">This playlist is empty or games could not be loaded.</p>
                    ) : (
                        // Style the game grid
                        <div className="game-grid grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            {playlistGames.map((game) => (
                                // Style the game card
                                <div className="card border rounded p-3 text-center shadow-sm" key={game.id || `${game.platform}-${game.title}`}>
                                    <img
                                        src={getImageUrl(game)}
                                        alt={`${game.title} Logo`}
                                        onError={(e) => (e.currentTarget.style.display = 'none')}
                                        // Style the game image
                                        className="mx-auto mb-2 max-h-24 object-contain" // Center, add margin, max height, object-contain
                                    />
                                    {/* Style the game title */}
                                    <p title={game.title} className="text-sm font-medium text-gray-800 truncate">{game.title || 'N/A'}</p> {/* Truncate long titles */}
                                    {/* Style the game platform */}
                                    <p className="text-xs text-gray-500 italic">{game.platform || 'N/A'}</p> {/* Smaller, gray, italic text */}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Playlists;

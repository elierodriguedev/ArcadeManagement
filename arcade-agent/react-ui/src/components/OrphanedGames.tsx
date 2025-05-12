import React, { useState, useEffect, useCallback } from 'react';

interface Game {
    id: string;
    title: string;
    platform: string;
    path: string;
}

interface PlaylistInfo { // Only need names
    name: string;
}

// Removed inline styles as we will use Tailwind classes
// const playlistSelectorStyle: React.CSSProperties = {
//     marginTop: '10px',
//     padding: '10px',
//     border: '1px solid #eee',
//     borderRadius: '4px',
//     backgroundColor: '#f9f9f9',
// };

// const playlistItemStyle: React.CSSProperties = {
//     padding: '5px',
//     cursor: 'pointer',
//     borderBottom: '1px solid #eee',
// };

// const playlistItemHoverStyle: React.CSSProperties = {
//     backgroundColor: '#e9ecef',
// };


const OrphanedGames: React.FC = () => {
    const [orphanedGames, setOrphanedGames] = useState<Game[]>([]);
    const [availablePlaylists, setAvailablePlaylists] = useState<string[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedGameId, setSelectedGameId] = useState<string | null>(null); // Track which game's playlist selector is open
    const [addingToPlaylist, setAddingToPlaylist] = useState<boolean>(false); // Loading state for API call

    const fetchOrphanedData = useCallback(async () => {
        setLoading(true);
        setError(null);
        setSelectedGameId(null); // Reset selection on refresh
        try {
            const [orphanedRes, playlistsRes] = await Promise.all([
                fetch('/api/launchbox/orphaned_games'),
                fetch('/api/launchbox/playlists')
            ]);

            if (!orphanedRes.ok) throw new Error(`Orphaned games fetch failed: HTTP error ${orphanedRes.status}`);
            if (!playlistsRes.ok) throw new Error(`Playlists fetch failed: HTTP error ${playlistsRes.status}`);

            const orphanedData: Game[] = await orphanedRes.json();
            const playlistsData: PlaylistInfo[] = await playlistsRes.json();

            setOrphanedGames(orphanedData);
            setAvailablePlaylists(playlistsData.map(p => p.name).sort()); // Sort playlist names

        } catch (err) {
            console.error("Error fetching orphaned games data:", err);
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
            setOrphanedGames([]);
            setAvailablePlaylists([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchOrphanedData();
    }, [fetchOrphanedData]);

    // Toggle playlist selector visibility for a game
    const handleCardClick = (gameId: string) => {
        setSelectedGameId(prevId => (prevId === gameId ? null : gameId)); // Toggle selection
    };

    // Add the selected game to the chosen playlist
    const handleAddToPlaylist = async (game: Game, targetPlaylistName: string) => {
        if (!game || !game.id || !targetPlaylistName) {
            alert("Error: Invalid game or playlist name.");
            return;
        }

        setAddingToPlaylist(true); // Show loading state
        console.log(`Attempting to add game ${game.id} (${game.title}) to playlist ${targetPlaylistName}`);
        try {
            const response = await fetch('/api/launchbox/playlists/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ playlist: targetPlaylistName, games: [game.id] }),
            });

            const result = await response.json();

            if (response.ok && (result.status === 'updated' || result.status === 'no changes')) {
                console.log(`Successfully added/verified game ${game.id} in playlist ${targetPlaylistName}.`);
                alert(`Game "${game.title}" added to playlist "${targetPlaylistName}".`);
                // Remove the game from the orphaned list in the UI
                setOrphanedGames(prev => prev.filter(g => g.id !== game.id));
                setSelectedGameId(null); // Close the selector
            } else {
                console.error(`Failed to add game to playlist:`, result);
                alert(`Error adding game: ${result.error || response.statusText || 'Unknown error'}`);
            }
        } catch (error) {
            console.error(`Network or other error adding game to playlist:`, error);
            alert(`Error adding game: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
             setAddingToPlaylist(false); // Hide loading state
        }
    };


    const getImageUrl = (game: Game): string => {
        const platformEncoded = encodeURIComponent(game.platform || '');
        const titleEncoded = encodeURIComponent(game.title || '');
        return `/img/${platformEncoded}/${titleEncoded}`;
    };

    if (loading) {
        return <div>Loading orphaned games...</div>;
    }

    if (error) {
        return <div style={{ color: 'red' }}>Error loading orphaned games: {error}</div>;
    }

    return (
        // Style the main container
        <div className="p-4 border rounded bg-white shadow-sm">
            {/* Style the heading */}
            <h3 className="text-lg font-semibold mb-3 text-gray-700">Orphaned Games ({orphanedGames.length})</h3>
            {/* Style the introductory paragraph */}
            <p className="mb-4 text-sm text-gray-600">Games not found in any playlist. Click a game to reveal options to add it to a playlist.</p>
            {loading ? (
                // Style loading message
                <p className="text-gray-600">Loading orphaned games...</p>
            ) : error ? (
                // Style error message
                <p className="text-red-500">Error loading orphaned games: {error}</p>
            ) : orphanedGames.length === 0 ? (
                // Style empty state message
                <p className="text-gray-600">No orphaned games found.</p>
            ) : (
                // Style the game grid
                <div className="game-grid grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {orphanedGames.map((game) => (
                        <div key={game.id || `${game.platform}-${game.title}`}>
                            <div
                                // Style the game card
                                className={`card border rounded p-3 text-center shadow-sm cursor-pointer hover:bg-gray-100 ${selectedGameId === game.id ? 'mb-0' : 'mb-4'}`} // Adjust margin if selector is open
                                onClick={() => handleCardClick(game.id)} // Toggle selector on card click
                                title={`Click to add "${game.title}" to a playlist`}
                            >
                                <img
                                    src={getImageUrl(game)}
                                    alt={`${game.title} Logo`}
                                    onError={(e) => (e.currentTarget.style.display = 'none')}
                                    // Style the game image
                                    className="mx-auto mb-2 max-h-24 object-contain" // Center, add margin, max height, object-contain
                                />
                                {/* Style the game title */}
                                <p title={game.title} className="text-sm font-medium text-gray-800 truncate">{game.title || 'N/A'}</p> {/* Add title attribute for long names, truncate */}
                                {/* Style the game platform */}
                                <p className="text-xs text-gray-500 italic"><em>({game.platform || 'N/A'})</em></p> {/* Smaller, gray, italic text */}
                            </div>

                            {/* Conditionally render the playlist selector */}
                            {selectedGameId === game.id && (
                                // Style the playlist selector popup
                                <div className="mt-2 p-3 border rounded bg-gray-50 shadow-inner">
                                    {addingToPlaylist ? (
                                        // Style adding message
                                        <p className="text-gray-600 text-sm">Adding...</p>
                                    ) : availablePlaylists.length > 0 ? (
                                        <>
                                            {/* Style "Add to:" label */}
                                            <p className="mb-2 text-sm font-semibold text-gray-700">Add to:</p>
                                            {availablePlaylists.map(playlistName => (
                                                <div
                                                    key={playlistName}
                                                    // Style playlist item
                                                    className="py-1 px-2 cursor-pointer border-b border-gray-200 text-gray-800 hover:bg-gray-200 text-sm last:border-b-0" // Add hover, text style, remove last border
                                                    onClick={() => handleAddToPlaylist(game, playlistName)}
                                                >
                                                    {playlistName}
                                                </div>
                                            ))}
                                        </>
                                    ) : (
                                        // Style no playlists message
                                        <p className="text-gray-600 text-sm">No playlists available.</p>
                                    )}
                                     {/* Style cancel button */}
                                     <button
                                        onClick={() => setSelectedGameId(null)}
                                        className="mt-3 px-3 py-1 bg-gray-300 text-gray-700 rounded text-xs hover:bg-gray-400 focus:outline-none" // Style button
                                     >
                                        Cancel
                                     </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default OrphanedGames;

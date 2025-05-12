import React, { useState, useEffect } from 'react';

interface Game {
    id: string;
    title: string;
    platform: string;
    path: string; // ApplicationPath
}

const GameList: React.FC = () => {
    const [games, setGames] = useState<Game[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [search, setSearch] = useState<string>("");

    // Filtered games based on search
    const filteredGames = games.filter(game => {
        const q = search.toLowerCase();
        return (
            game.title.toLowerCase().includes(q) ||
            game.platform.toLowerCase().includes(q)
        );
    });

    useEffect(() => {
        const fetchGames = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch('/api/launchbox/games');
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                const data: Game[] = await response.json();
                setGames(data);
            } catch (err) {
                console.error("Error fetching game list:", err);
                setError(err instanceof Error ? err.message : 'An unknown error occurred');
                setGames([]); // Clear games on error
            } finally {
                setLoading(false);
            }
        };

        fetchGames();
    }, []); // Fetch only once on mount

    const getImageUrl = (game: Game): string => {
        // Basic encoding, might need more robust handling depending on characters
        const platformEncoded = encodeURIComponent(game.platform || '');
        const titleEncoded = encodeURIComponent(game.title || '');
        return `/img/${platformEncoded}/${titleEncoded}`;
    };

    if (loading) {
        // Style loading message
        return <div className="text-gray-600 p-4">Loading game list...</div>;
    }

    if (error) {
        // Style error message
        return <div className="text-red-500 p-4">Error loading game list: {error}</div>;
    }

    return (
        // Style the main container
        <div className="p-4 border rounded bg-white shadow-sm">
            {/* Style the heading */}
            <h3 className="text-lg font-semibold mb-3 text-gray-700">Game List ({filteredGames.length})</h3>
            {/* Style the search input container and input */}
            <div className="mb-4">
                <input
                    type="text"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    placeholder="Search games or platforms..."
                    // Apply Tailwind classes for styling
                    className="w-full max-w-sm mx-auto p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                />
            </div>
            {filteredGames.length === 0 ? (
                // Style empty state message
                <p className="text-gray-600 text-center">No games found.</p>
            ) : (
                // Style the game grid
                <div className="game-grid grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {filteredGames.map((game) => (
                        // Style the game card
                        <div className="card border rounded p-3 text-center shadow-sm" key={game.id || `${game.platform}-${game.title}`}> {/* Use ID if available, fallback otherwise */}
                            <img
                                src={getImageUrl(game)}
                                alt={`${game.title} Logo`}
                                onError={(e) => (e.currentTarget.style.display = 'none')} // Hide img on error
                                // Style the game image
                                className="mx-auto mb-2 max-h-24 object-contain" // Center, add margin, max height, object-contain
                            />
                            {/* Style the game title */}
                            <p title={game.title} className="text-sm font-medium text-gray-800 truncate">{game.title || 'N/A'}</p> {/* Add title attribute for long names, truncate */}
                            {/* Style the platform span */}
                            <span className="platform text-xs text-gray-500 italic">{game.platform || 'N/A'}</span> {/* Smaller, gray, italic text */}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default GameList;

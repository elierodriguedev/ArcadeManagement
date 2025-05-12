import React from 'react';
import { Tabs, Tab } from './Tabs';
import Playlists from './Playlists';
import GameList from './GameList';
import OrphanedGames from './OrphanedGames';
import ArcadeControlsTab from './ArcadeControlsTab'; // Import the new controls tab component

const ArcadeTab: React.FC = () => {
  return (
    // Add padding to the container
    <div className="p-4">
      {/* Style the heading */}
      <h2 className="text-xl font-bold mb-4 text-gray-700">Arcade Management</h2>
      <Tabs>
        <Tab label="Playlists" icon="▶️">
          <Playlists />
        </Tab>
        <Tab label="Games" icon="🎮">
          <GameList />
        </Tab>
        <Tab label="Orphaned Games" icon="👻">
          <OrphanedGames />
        </Tab>
        <Tab label="Controls" icon="⚙️"> {/* Add the new Controls tab */}
          <ArcadeControlsTab />
        </Tab>
      </Tabs>
    </div>
  );
};

export default ArcadeTab;
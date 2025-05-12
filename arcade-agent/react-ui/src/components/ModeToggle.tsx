import React from 'react';

interface ModeToggleProps {
  currentMode: 'Arcade' | 'Pinball';
  onToggle: (mode: 'Arcade' | 'Pinball') => void;
}

const ModeToggle: React.FC<ModeToggleProps> = ({ currentMode, onToggle }) => {
  const buttonBaseStyle = "px-3 py-1 rounded text-sm focus:outline-none";
  const activeStyle = "bg-blue-500 text-white";
  const inactiveStyle = "bg-gray-200 text-gray-700 hover:bg-gray-300";

  return (
    // Apply flex layout, spacing, and margin
    <div className="flex items-center space-x-2 mb-4">
      {/* Style the label */}
      <span className="font-semibold text-gray-700">Mode:</span>
      <button
        // Apply base style + conditional active/inactive styles
        className={`${buttonBaseStyle} ${currentMode === 'Arcade' ? activeStyle : inactiveStyle}`}
        onClick={() => onToggle('Arcade')}
      >
        Arcade
      </button>
      <button
        // Apply base style + conditional active/inactive styles
        className={`${buttonBaseStyle} ${currentMode === 'Pinball' ? activeStyle : inactiveStyle}`}
        onClick={() => onToggle('Pinball')}
      >
        Pinball
      </button>
    </div>
  );
};

export default ModeToggle;
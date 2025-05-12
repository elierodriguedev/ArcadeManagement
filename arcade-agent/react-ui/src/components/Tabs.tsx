import React, { useState } from 'react';

interface TabProps {
  label: string;
  icon?: React.ReactNode; // Added optional icon prop
  children: React.ReactNode;
}

export const Tab: React.FC<TabProps> = ({ children }) => {
  return <div>{children}</div>;
};

interface TabsProps {
  children: React.ReactElement<TabProps>[];
}

export const Tabs: React.FC<TabsProps> = ({ children }) => {
  const [activeTab, setActiveTab] = useState(children[0].props.label);

  return (
    <div className="tabs"> {/* Added a wrapper class for clarity */}
      {/* Apply flex, spacing, and border like the controller */}
      <div className="tab-buttons flex space-x-4 border-b border-gray-200">
        {children.map((child) => {
          const { label, icon } = child.props; // Destructure icon here
          const isActive = activeTab === label;
          return (
            <button
              key={label}
              // Apply base button styles + active styles conditionally
              className={`tab-button flex items-center px-4 py-2 text-gray-600 hover:text-blue-500 focus:outline-none ${
                isActive ? 'text-blue-500 border-b-2 border-blue-500' : 'border-b-2 border-transparent'
              }`}
              onClick={() => setActiveTab(label)}
            >
              {/* Use flex utilities, remove inline styles */}
              {icon && <span className="mr-2">{icon}</span>} {/* Add margin utility */}
              {label}
            </button>
          );
        })}
      </div>
      {/* Add margin-top to content area */}
      <div className="tab-content mt-4">
        {children.map((child) => {
          if (child.props.label === activeTab) {
            return <div key={child.props.label}>{child.props.children}</div>;
          }
          return null;
        })}
      </div>
    </div>
  );
};
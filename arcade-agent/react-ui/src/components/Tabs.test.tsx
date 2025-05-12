import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom'; // Import jest-dom matchers
import userEvent from '@testing-library/user-event'; // Import userEvent
import { Tabs, Tab } from './Tabs'; // Assuming Tabs component is in Tabs.tsx

describe('Tabs', () => {
  test('renders main tabs correctly', () => {
    render(
      <Tabs>
        <Tab label="Server">Server Content</Tab>
        <Tab label="Arcade">Arcade Content</Tab>
        <Tab label="Pinball">Pinball Content</Tab>
      </Tabs>
    );

    // Check if main tabs are rendered
    expect(screen.getByText('Server')).toBeInTheDocument();
    expect(screen.getByText('Arcade')).toBeInTheDocument();
    expect(screen.getByText('Pinball')).toBeInTheDocument();
  });

  test('switches between main tabs correctly on click', async () => {
    render(
      <Tabs>
        <Tab label="Server">Server Content</Tab>
        <Tab label="Arcade">Arcade Content</Tab>
        <Tab label="Pinball">Pinball Content</Tab>
      </Tabs>
    );

    // Initial state: Server tab content should be visible
    expect(screen.getByText('Server Content')).toBeVisible();
    expect(screen.queryByText('Arcade Content')).not.toBeInTheDocument();
    expect(screen.queryByText('Pinball Content')).not.toBeInTheDocument();

    // Click on Arcade tab
    const arcadeTabButton = screen.getByText('Arcade');
    await userEvent.click(arcadeTabButton);

    // Arcade tab content should be visible, others should be hidden
    expect(screen.queryByText('Server Content')).not.toBeInTheDocument();
    expect(screen.getByText('Arcade Content')).toBeVisible();
    expect(screen.queryByText('Pinball Content')).not.toBeInTheDocument();

    // Click on Pinball tab
    const pinballTabButton = screen.getByText('Pinball');
    await userEvent.click(pinballTabButton);

    // Pinball tab content should be visible, others should be hidden
    expect(screen.queryByText('Server Content')).not.toBeInTheDocument();
    expect(screen.queryByText('Arcade Content')).not.toBeInTheDocument();
    expect(screen.getByText('Pinball Content')).toBeVisible();
  });
});
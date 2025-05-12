import { render, screen, waitFor } from '@testing-library/react'; // Import waitFor
import '@testing-library/jest-dom';
import ServerTab from './ServerTab'; // Assuming ServerTab component is in ServerTab.tsx
import fetchMock from 'jest-fetch-mock'; // Import fetchMock
import userEvent from '@testing-library/user-event'; // Import userEvent

describe('ServerTab', () => {
  const mockProps = {
    logs: [],
    logConnectionStatus: true,
    updateStatus: 'idle' as const,
    handleCheckForUpdate: jest.fn(), // This seems like it should be onCheckForUpdate based on App.tsx
    currentMode: 'Arcade' as const,
    onModeToggle: jest.fn(),
    onCheckForUpdate: jest.fn(), // Add mock for onCheckForUpdate
  };

  beforeEach(() => {
    fetchMock.resetMocks(); // Reset mocks before each test
  });

  test('renders sub-tabs correctly', async () => { // Made test async
    const mockStatusData = {
      cpu_usage: 10,
      memory_usage: 20,
      disk_usage: 30,
      // Add other properties as needed by SystemStatus
    };
    fetchMock.mockResponseOnce(JSON.stringify(mockStatusData)); // Mock the fetch call

    render(<ServerTab {...mockProps} />);

    // Check if sub-tabs are rendered
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Log')).toBeInTheDocument();
    expect(screen.getByText('Screenshot')).toBeInTheDocument();
    expect(screen.getByText('Image Generation')).toBeInTheDocument();
    expect(screen.getByText('Check for Update')).toBeInTheDocument();

    // Wait for the SystemStatus component to finish fetching and rendering
    await waitFor(() => {
      expect(screen.getByText(/CPU Usage:/)).toBeInTheDocument(); // Check for content from SystemStatus
    });
  });

  const mockStatusData = {
    status: 'Online',
    type: 'Agent',
    hostname: 'TestHost',
    version: '1.0.0',
    disk_total_gb: 100,
    disk_free_gb: 50,
    cpu_percent: 10,
    ram_percent: 20,
    bigbox_running: false,
  };

  test('switches between sub-tabs and renders correct components', async () => {
    // Mock fetch calls in the order they are expected to occur
    fetchMock.mockResponseOnce(JSON.stringify(mockStatusData), { status: 200 }); // Mock /api/ping for SystemStatus

    // Mock a simple image response (a 1x1 transparent PNG) for ScreenshotViewer
    const pngData = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
    const byteCharacters = atob(pngData);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'image/png' });
    fetchMock.mockResponseOnce(blob as any, { status: 200 }); // Mock /api/screenshot for ScreenshotViewer, cast to any

    // Mock image generation response for ImageGenerator
    fetchMock.mockResponseOnce(JSON.stringify({ imageUrl: 'mock-image-url' }), { status: 200 }); // Mock /api/generate-image for ImageGenerator


    render(<ServerTab {...mockProps} />);

    // Wait for the initial fetch in SystemStatus to complete
    await waitFor(() => {
      expect(screen.getByText('System Status')).toBeInTheDocument();
    });

    // Initial state: Status tab content should be visible, others not in document
    expect(screen.getByRole('heading', { name: 'System Status' })).toBeInTheDocument(); // SystemStatus content
    expect(screen.queryByRole('heading', { name: 'Agent Log' })).not.toBeInTheDocument(); // LogViewer content
    expect(screen.queryByRole('heading', { name: 'Live Screenshot' })).not.toBeInTheDocument(); // ScreenshotViewer content
    expect(screen.queryByRole('heading', { name: 'Image Generation' })).not.toBeInTheDocument(); // ImageGenerator content
    expect(screen.queryByRole('heading', { name: 'Update Agent' })).not.toBeInTheDocument(); // AgentUpdate content


    // Click on Log tab
    const logTabButton = screen.getByText('Log');
    await userEvent.click(logTabButton);

    // Log tab content should be visible, others not in document
    expect(screen.queryByRole('heading', { name: 'System Status' })).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Agent Log' })).toBeInTheDocument(); // LogViewer content
    expect(screen.queryByRole('heading', { name: 'Live Screenshot' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Image Generation' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Update Agent' })).not.toBeInTheDocument();

    // Click on Screenshot tab
    const screenshotTabButton = screen.getByText('Screenshot');
    await userEvent.click(screenshotTabButton);

    // Screenshot tab content should be visible, others not in document
    expect(screen.queryByRole('heading', { name: 'System Status' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Agent Log' })).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Live Screenshot' })).toBeInTheDocument(); // ScreenshotViewer content
    expect(screen.queryByRole('heading', { name: 'Image Generation' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Update Agent' })).not.toBeInTheDocument();

    // Click on Image Generation tab
    const imageGenTabButton = screen.getByText('Image Generation');
    await userEvent.click(imageGenTabButton);

    // Image Generation tab content should be visible, others not in document
    expect(screen.queryByRole('heading', { name: 'System Status' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Agent Log' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Live Screenshot' })).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Image Generation' })).toBeInTheDocument(); // ImageGenerator content
    expect(screen.queryByRole('heading', { name: 'Update Agent' })).not.toBeInTheDocument();

    // Click on Check for Update tab
    const updateTabButton = screen.getByText('Check for Update');
    await userEvent.click(updateTabButton);

    // Check for Update tab content should be visible, others not in document
    expect(screen.queryByRole('heading', { name: 'System Status' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Agent Log' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Live Screenshot' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Image Generation' })).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Update Agent' })).toBeInTheDocument(); // AgentUpdate content
  });
});
import { render, screen, waitFor } from '@testing-library/react'; // Import waitFor
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event'; // Import userEvent
import ArcadeTab from './ArcadeTab'; // Assuming ArcadeTab component is in ArcadeTab.tsx
import fetchMock from 'jest-fetch-mock'; // Import fetchMock

describe('ArcadeTab', () => {
  beforeEach(() => {
    fetchMock.resetMocks(); // Reset mocks before each test
  });

  test('renders sub-tabs correctly', async () => { // Made test async
    // Mock fetch calls for default active tab (Playlists)
    fetchMock.mockResponseOnce(JSON.stringify([{ name: 'Playlist 1' }, { name: 'Playlist 2' }]), { status: 200 }); // Mock /api/launchbox/playlists

    render(<ArcadeTab />);

    // Check if sub-tabs are rendered (using getByText is fine for the buttons)
    expect(screen.getAllByText('Playlists').length).toBe(2); // One button, one heading
    expect(screen.getByText('Games')).toBeInTheDocument();
    expect(screen.getByText('Orphaned Games')).toBeInTheDocument();

    // Wait for the initial fetch in Playlists to complete and check for its content
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Playlists' })).toBeInTheDocument();
    });
  });

  test('switches between sub-tabs and renders correct components', async () => {
    // Mock fetch calls for all components in the order they are expected to be rendered
    fetchMock.mockResponseOnce(JSON.stringify([{ name: 'Playlist 1' }, { name: 'Playlist 2' }]), { status: 200 }); // Mock /api/launchbox/playlists for Playlists tab
    fetchMock.mockResponseOnce(JSON.stringify([{ id: '1', title: 'Game 1', platform: 'Platform 1', path: '' }]), { status: 200 }); // Mock /api/launchbox/games for Games tab
    fetchMock.mockResponseOnce(JSON.stringify([{ id: 'o1', title: 'Orphaned 1', platform: 'Orphaned Platform', path: '' }]), { status: 200 }); // Mock /api/launchbox/orphaned_games for Orphaned Games tab
    fetchMock.mockResponseOnce(JSON.stringify([{ name: 'Playlist A' }]), { status: 200 }); // Mock /api/launchbox/playlists for Orphaned Games tab


    render(<ArcadeTab />);

    // Wait for the initial fetch in Playlists to complete
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Playlists' })).toBeInTheDocument();
    });

    // Initial state: Playlists tab content visible, others not in document
    expect(screen.getByRole('heading', { name: 'Playlists' })).toBeInTheDocument(); // Playlists content
    expect(screen.queryByRole('heading', { name: 'Game List' })).not.toBeInTheDocument(); // GameList content
    expect(screen.queryByRole('heading', { name: 'Orphaned Games' })).not.toBeInTheDocument(); // OrphanedGames content

    // Click on Games tab
    const gamesTabButton = screen.getByText('Games');
    await userEvent.click(gamesTabButton);

    // Games tab content visible, others not in document
    expect(screen.queryByRole('heading', { name: 'Playlists' })).not.toBeInTheDocument();
    // Wait for the fetch in GameList to complete and check for its content
    await waitFor(() => {
        expect(screen.getByRole('heading', { name: /Game List/ })).toBeInTheDocument(); // GameList content
    });
    expect(screen.queryByRole('heading', { name: 'Orphaned Games' })).not.toBeInTheDocument();

    // Click on Orphaned Games tab
    const orphanedGamesTabButton = screen.getByText('Orphaned Games');
    await userEvent.click(orphanedGamesTabButton);

    // Orphaned Games tab content visible, others not in document
    expect(screen.queryByRole('heading', { name: 'Playlists' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Game List' })).not.toBeInTheDocument();
     // Wait for the fetches in OrphanedGames to complete and check for its content
    await waitFor(() => {
        expect(screen.getByRole('heading', { name: /Orphaned Games/ })).toBeInTheDocument(); // OrphanedGames content
    });
  });
});
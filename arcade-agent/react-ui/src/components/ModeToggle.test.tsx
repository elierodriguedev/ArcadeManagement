import { render, screen, fireEvent, act } from '@testing-library/react'; // Import fireEvent and act
import { userEvent } from '@testing-library/user-event'; // Import userEvent
import '@testing-library/jest-dom';
import ModeToggle from './ModeToggle'; // Assuming ModeToggle component is in ModeToggle.tsx

describe('ModeToggle', () => {
  const mockOnToggle = jest.fn();

  test('renders with Arcade mode active', async () => {
    await render(<ModeToggle currentMode="Arcade" onToggle={mockOnToggle} />);

    const arcadeButton = screen.getByText('Arcade');
    const pinballButton = screen.getByText('Pinball');

    expect(arcadeButton).toHaveClass('active');
    expect(pinballButton).not.toHaveClass('active');
  });

  test('renders with Pinball mode active', async () => {
    await render(<ModeToggle currentMode="Pinball" onToggle={mockOnToggle} />);

    const arcadeButton = screen.getByText('Arcade');
    const pinballButton = screen.getByText('Pinball');

    expect(arcadeButton).not.toHaveClass('active');
    expect(pinballButton).toHaveClass('active');
  });
  test('calls onToggle with "Pinball" when Pinball button is clicked in Arcade mode', async () => {
    await render(<ModeToggle currentMode="Arcade" onToggle={mockOnToggle} />);

    // Click the Pinball button
    const pinballButton = screen.getByRole('button', { name: 'Pinball' });
    act(() => {
      fireEvent.click(pinballButton);
    });

    // Expect onToggle to have been called with 'Pinball'
    expect(mockOnToggle).toHaveBeenCalledTimes(1);
    expect(mockOnToggle).toHaveBeenCalledWith('Pinball');
  });

  test('calls onToggle with "Arcade" when Arcade button is clicked in Pinball mode', async () => {
    await render(<ModeToggle currentMode="Pinball" onToggle={mockOnToggle} />);

    // Click the Arcade button
    const arcadeButton = screen.getByRole('button', { name: 'Arcade' });
    // Use userEvent to click the button
    await userEvent.click(arcadeButton);

    // Expect onToggle to have been called with 'Arcade'
    expect(mockOnToggle).toHaveBeenCalledTimes(1);
    expect(mockOnToggle).toHaveBeenCalledWith('Arcade');
  });
});
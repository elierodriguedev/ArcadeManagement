import fetchMock from 'jest-fetch-mock';

fetchMock.enableMocks();

// Mock URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'mock-object-url');
global.URL.revokeObjectURL = jest.fn(); // Also mock revokeObjectURL
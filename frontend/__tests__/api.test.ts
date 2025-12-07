/**
 * Tests for API client
 */
import apiClient from '../lib/api';

// Mock axios
jest.mock('axios', () => {
  const mockAxios = {
    create: jest.fn(() => ({
      interceptors: {
        request: { use: jest.fn() },
        response: { use: jest.fn() },
      },
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      delete: jest.fn(),
    })),
    post: jest.fn(),
  };
  return mockAxios;
});

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear localStorage
    if (typeof window !== 'undefined') {
      localStorage.clear();
    }
  });

  it('should have instance method', () => {
    expect(apiClient.instance).toBeDefined();
  });

  it('should set token in localStorage', () => {
    if (typeof window !== 'undefined') {
      apiClient.setToken('test-token');
      expect(localStorage.getItem('access_token')).toBe('test-token');
    }
  });

  it('should set refresh token in localStorage', () => {
    if (typeof window !== 'undefined') {
      apiClient.setRefreshToken('test-refresh-token');
      expect(localStorage.getItem('refresh_token')).toBe('test-refresh-token');
    }
  });

  it('should clear tokens from localStorage', () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', 'test-token');
      localStorage.setItem('refresh_token', 'test-refresh-token');
      apiClient.clearToken();
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
    }
  });
});

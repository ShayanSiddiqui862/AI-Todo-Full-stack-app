'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api, { ApiResponse } from '../lib/api';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthResponse {
  token: string;
  user?: User;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (email: string, password: string, name: string) => Promise<boolean>;
  logout: () => void;
  checkAuthStatus: () => Promise<void>;
  loginWithGoogle: () => Promise<boolean>;
}

interface TokenData {
  access_token: string;
  refresh_token: string;
  token_type?: string;
  expires_in?: number;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check authentication status on initial load
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      api.setToken(token);
      checkAuthStatus();
    } else {
      setIsLoading(false);
    }
  }, []);

  const checkAuthStatus = async () => {
    try {
      setIsLoading(true);
      // Validate token with backend
      const response = await api.getUserProfile();
      if (response.success && response.data) {
        setUser(response.data as User);
        setIsAuthenticated(true);
      } else {
        // Token might be expired, try to refresh
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const refreshResponse = await api.refreshToken(refreshToken);
          if (refreshResponse.success && refreshResponse.data) {
            // Store new tokens
            const newTokenData = refreshResponse.data as TokenData;
            localStorage.setItem('authToken', newTokenData.access_token);
            localStorage.setItem('refreshToken', newTokenData.refresh_token);
            api.setToken(newTokenData.access_token);

            // Get user profile with new token
            const profileResponse = await api.getUserProfile();
            if (profileResponse.success && profileResponse.data) {
              setUser(profileResponse.data as User);
              setIsAuthenticated(true);
            } else {
              // Still failed after refresh, clear tokens
              clearAuthTokens();
            }
          } else {
            // Refresh failed, clear tokens
            clearAuthTokens();
          }
        } else {
          // No refresh token, clear tokens
          clearAuthTokens();
        }
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      // Check if it's a token expiration issue
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          // Try to refresh the token
          const refreshResponse = await api.refreshToken(refreshToken);
          if (refreshResponse.success && refreshResponse.data) {
            // Store new tokens
            const newTokenData = refreshResponse.data as TokenData;
            localStorage.setItem('authToken', newTokenData.access_token);
            localStorage.setItem('refreshToken', newTokenData.refresh_token);
            api.setToken(newTokenData.access_token);

            // Get user profile with new token
            const profileResponse = await api.getUserProfile();
            if (profileResponse.success && profileResponse.data) {
              setUser(profileResponse.data as User);
              setIsAuthenticated(true);
            } else {
              clearAuthTokens();
            }
          } else {
            clearAuthTokens();
          }
        } catch (refreshError) {
          clearAuthTokens();
        }
      } else {
        clearAuthTokens();
      }
    } finally {
      setIsLoading(false);
    }
  };

  const clearAuthTokens = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    api.removeToken();
    setIsAuthenticated(false);
    setUser(null);
  };

  const loginWithGoogle = async (): Promise<boolean> => {
    try {
      setIsLoading(true);
      // First, get the Google auth URL from the backend
      const response = await api.initiateGoogleAuth();

      if (response.success && response.data) {
        // Redirect the user to Google's OAuth page
        const tokenData = response.data as TokenData & { auth_url: string };
        window.location.href = tokenData.auth_url;
        return true;
      } else {
        console.error('Failed to get Google auth URL');
        return false;
      }
    } catch (error) {
      console.error('Error initiating Google auth:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      // For login, we'll use the email as the username since backend expects username
      const response = await api.login(email, password);

      if (response.success && response.data) {
        // Backend returns: {access_token, refresh_token, token_type, expires_in}
        const tokenData = response.data as TokenData;
        if (tokenData.access_token) {
          // Store tokens in localStorage
          localStorage.setItem('authToken', tokenData.access_token);
          localStorage.setItem('refreshToken', tokenData.refresh_token);
          api.setToken(tokenData.access_token);

          // Get user profile
          const profileResponse = await api.getUserProfile();
          if (profileResponse.success && profileResponse.data) {
            setUser(profileResponse.data as User);
            setIsAuthenticated(true);
            return true;
          }
        }
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email: string, password: string, name: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      const response = await api.signup(email, password, name);

      if (response.success && response.data) {
        // Backend returns: {access_token, refresh_token, token_type, expires_in}
        const tokenData = response.data as TokenData;
        if (tokenData.access_token) {
          // Store tokens in localStorage
          localStorage.setItem('authToken', tokenData.access_token);
          localStorage.setItem('refreshToken', tokenData.refresh_token);
          api.setToken(tokenData.access_token);

          // Get user profile
          const profileResponse = await api.getUserProfile();
          if (profileResponse.success && profileResponse.data) {
            setUser(profileResponse.data as User);
            setIsAuthenticated(true);
            return true;
          }
        }
      }
      return false;
    } catch (error) {
      console.error('Signup error:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (): void => {
    try {
      // Get refresh token from localStorage for logout
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        // Call the backend logout endpoint with refresh token
        api.logout(refreshToken).catch((error) => {
          console.error('Logout error:', error);
        });
      }
    } finally {
      // Remove tokens from localStorage and API client
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('tasks'); // Clear offline tasks on logout
      api.removeToken();

      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    signup,
    logout,
    checkAuthStatus,
    loginWithGoogle
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { AuthApiClient } from "../lib/api";
import { AuthContextValue, User, ApiError, TwoFactorLoginResponse } from "../lib/types";

const AuthContext = createContext<AuthContextValue | null>(null);

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
  apiBaseUrl: string;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({
  children,
  apiBaseUrl,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [apiClient] = useState(() => new AuthApiClient(apiBaseUrl));

  const refreshUser = useCallback(async () => {
    try {
      const userData = await apiClient.getCurrentUser();
      setUser(userData.user);
    } catch (error) {
      setUser(null);
      // Silently fail for initial load - user might not be authenticated
    }
  }, [apiClient]);

  const login = useCallback(
    async (email: string, password: string, recaptchaToken?: string): Promise<TwoFactorLoginResponse> => {
      setIsLoading(true);
      try {
        const response = await apiClient.login(email, password, recaptchaToken);
        
        // If 2FA is not required, set user immediately
        if (!response.requires_2fa && response.user) {
          setUser(response.user);
        }
        
        return response;
      } catch (error) {
        const apiError = error as ApiError;
        throw new Error(apiError.message);
      } finally {
        setIsLoading(false);
      }
    },
    [apiClient]
  );

  const signup = useCallback(
    async (email: string, password: string, name?: string, recaptchaToken?: string) => {
      setIsLoading(true);
      try {
        const userData = await apiClient.signup(email, password, name, recaptchaToken);
        setUser(userData.user);
      } catch (error) {
        const apiError = error as ApiError;
        throw new Error(apiError.message);
      } finally {
        setIsLoading(false);
      }
    },
    [apiClient]
  );

  const googleLoginWithCredential = useCallback(
    async (credential: string) => {
      setIsLoading(true);
      try {
        const userData = await apiClient.googleLogin(credential);
        setUser(userData.user);
      } catch (error) {
        const apiError = error as ApiError;
        throw new Error(apiError.message);
      } finally {
        setIsLoading(false);
      }
    },
    [apiClient]
  );

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await apiClient.logout();
      setUser(null);
    } catch (error) {
      // Even if logout fails on server, clear local state
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [apiClient]);

  const completeTwoFactorLogin = useCallback((user: User) => {
    setUser(user);
  }, []);

  // Load user on mount
  useEffect(() => {
    const loadUser = async () => {
      setIsLoading(true);
      await refreshUser();
      setIsLoading(false);
    };
    loadUser();
  }, [refreshUser]);

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    signup,
    googleLoginWithCredential,
    logout,
    refreshUser,
    completeTwoFactorLogin,
    apiClient,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

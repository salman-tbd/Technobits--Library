export interface User {
  id: number;
  email: string;
  name?: string;
}

export interface AuthResponse {
  user: User;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name?: string) => Promise<void>;
  googleLoginWithCredential: (credential: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  apiClient: any; // AuthApiClient - using any to avoid circular import
}

export interface AuthContextValue extends AuthState, AuthActions {}

export interface AuthProviderProps {
  children: React.ReactNode;
  apiBaseUrl: string;
}

export interface LoginFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  onForgotPasswordSuccess?: (message: string) => void;
  className?: string;
}

export interface SignupFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  className?: string;
}

export interface GoogleButtonProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  className?: string;
  text?: string;
}

export interface ApiError {
  message: string;
  details?: Record<string, string[]>;
}

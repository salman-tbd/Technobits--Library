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
  login: (email: string, password: string, recaptchaToken?: string) => Promise<TwoFactorLoginResponse>;
  signup: (email: string, password: string, name?: string, recaptchaToken?: string) => Promise<void>;
  googleLoginWithCredential: (credential: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  completeTwoFactorLogin: (user: User) => void;
  apiClient: any; // AuthApiClient - using any to avoid circular import
}

export interface AuthContextValue extends AuthState, AuthActions {}

export interface AuthProviderProps {
  children: React.ReactNode;
  apiBaseUrl: string;
}

export interface LoginFormProps {
  onSuccess?: () => void;
  onLoginResponse?: (response: TwoFactorLoginResponse) => void;
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

// Two-Factor Authentication Types
export interface TwoFactorSetupResponse {
  secret_key: string;
  qr_code_uri: string;
  qr_code_image: string;
  message: string;
}

export interface TwoFactorEnableResponse {
  message: string;
  backup_codes: string[];
  backup_codes_message: string;
}

export interface TwoFactorVerifyResponse {
  message: string;
  verification_method: 'totp' | 'backup';
  remaining_backup_codes?: number;
}

export interface TwoFactorStatus {
  is_enabled: boolean;
  backup_tokens_count: number;
  last_used_at: string | null;
}

export interface TwoFactorLoginResponse {
  requires_2fa: boolean;
  temp_token?: string;
  user_id?: number;
  message: string;
  backup_codes_available?: boolean;
  user?: User;
}

export interface TwoFactorRateLimitError {
  error: string;
  rate_limited: boolean;
  remaining_attempts: number;
  lockout_ends_at?: string;
  rate_limit_message?: string;
}

// Component Props
export interface TwoFactorSetupProps {
  onSuccess?: (backupCodes: string[]) => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
  className?: string;
}

export interface TwoFactorVerifyProps {
  onSuccess?: (method: 'totp' | 'backup') => void;
  onError?: (error: string) => void;
  showBackupOption?: boolean;
  className?: string;
}

export interface TwoFactorLoginVerifyProps {
  tempToken: string;
  userId: number;
  backupCodesAvailable: boolean;
  onSuccess?: (user: User) => void;
  onError?: (error: string) => void;
  className?: string;
}

export interface BackupCodesDisplayProps {
  codes: string[];
  onDownload?: () => void;
  onClose?: () => void;
  className?: string;
}

export interface TwoFactorSettingsProps {
  onStatusChange?: (enabled: boolean) => void;
  className?: string;
}

export interface QRCodeDisplayProps {
  qrCodeImage: string;
  secretKey: string;
  onContinue?: () => void;
  className?: string;
}
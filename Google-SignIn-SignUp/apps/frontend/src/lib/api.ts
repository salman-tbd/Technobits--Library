import { 
  ApiError, 
  User, 
  AuthResponse, 
  TwoFactorSetupResponse,
  TwoFactorEnableResponse,
  TwoFactorVerifyResponse,
  TwoFactorStatus,
  TwoFactorLoginResponse
} from "./types";

export class AuthApiClient {
  constructor(private baseUrl: string) {}

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let errorDetails: Record<string, string[]> | undefined;

      try {
        const errorData = await response.json();
        if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.non_field_errors) {
          errorMessage = errorData.non_field_errors[0];
        }
        errorDetails = errorData;
      } catch {
        // Use default error message if JSON parsing fails
      }

      const error: ApiError = { message: errorMessage, details: errorDetails };
      throw error;
    }

    // Handle empty responses (like logout)
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return response.json();
    }
    
    return {} as T;
  }

  async login(email: string, password: string, recaptchaToken?: string): Promise<TwoFactorLoginResponse> {
    const payload: any = { email, password };
    if (recaptchaToken) {
      payload.recaptcha_token = recaptchaToken;
    }
    return this.request<TwoFactorLoginResponse>("/auth/login/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async signup(email: string, password: string, name?: string, recaptchaToken?: string): Promise<AuthResponse> {
    const payload: any = { email, password };
    if (name) payload.name = name;
    if (recaptchaToken) payload.recaptcha_token = recaptchaToken;
    return this.request<AuthResponse>("/auth/register/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async googleLogin(credential: string): Promise<AuthResponse> {
    return this.request<AuthResponse>("/auth/google/", {
      method: "POST",
      body: JSON.stringify({ credential }),
    });
  }

  async getCurrentUser(): Promise<AuthResponse> {
    return this.request<AuthResponse>("/auth/me/");
  }

  async logout(): Promise<void> {
    return this.request<void>("/auth/logout/", {
      method: "POST",
    });
  }

  async refreshToken(): Promise<void> {
    return this.request<void>("/auth/refresh/", {
      method: "POST",
    });
  }

  async forgotPassword(email: string, recaptchaToken?: string): Promise<{ message: string }> {
    const payload: any = { email };
    if (recaptchaToken) payload.recaptcha_token = recaptchaToken;
    return this.request<{ message: string }>("/auth/forgot-password/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async resetPassword(token: string, password: string, recaptchaToken?: string): Promise<{ message: string }> {
    const payload: any = { token, password };
    if (recaptchaToken) payload.recaptcha_token = recaptchaToken;
    return this.request<{ message: string }>("/auth/reset-password/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Two-Factor Authentication Methods

  async twoFactorSetup(): Promise<TwoFactorSetupResponse> {
    return this.request<TwoFactorSetupResponse>("/auth/2fa/setup/", {
      method: "POST",
    });
  }

  async twoFactorEnable(totpCode: string): Promise<TwoFactorEnableResponse> {
    return this.request<TwoFactorEnableResponse>("/auth/2fa/enable/", {
      method: "POST",
      body: JSON.stringify({ totp_code: totpCode }),
    });
  }

  async twoFactorVerify(totpCode?: string, backupCode?: string): Promise<TwoFactorVerifyResponse> {
    const payload: any = {};
    if (totpCode) payload.totp_code = totpCode;
    if (backupCode) payload.backup_code = backupCode;
    
    return this.request<TwoFactorVerifyResponse>("/auth/2fa/verify/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async twoFactorDisable(password: string, totpCode?: string, backupCode?: string): Promise<{ message: string }> {
    const payload: any = { password };
    if (totpCode) payload.totp_code = totpCode;
    if (backupCode) payload.backup_code = backupCode;
    
    return this.request<{ message: string }>("/auth/2fa/disable/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async twoFactorStatus(): Promise<TwoFactorStatus> {
    return this.request<TwoFactorStatus>("/auth/2fa/status/");
  }

  async twoFactorLoginComplete(
    tempToken: string, 
    userId: number, 
    totpCode?: string, 
    backupCode?: string
  ): Promise<AuthResponse> {
    const payload: any = {
      temp_token: tempToken,
      user_id: userId,
    };
    if (totpCode) payload.totp_code = totpCode;
    if (backupCode) payload.backup_code = backupCode;
    
    return this.request<AuthResponse>("/auth/login/2fa-complete/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }
}

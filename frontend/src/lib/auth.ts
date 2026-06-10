import { browser } from '$app/environment';

const USER_STORAGE_KEY = 'face-presensi-user';
const TOKEN_STORAGE_KEY = 'face-presensi-token';

export type AuthUser = {
  id: string;
  email: string;
  name: string;
  role: string;
};

export function getStoredUser(): AuthUser | null {
  if (!browser) return null;
  const raw = localStorage.getItem(USER_STORAGE_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function getStoredToken(): string | null {
  if (!browser) return null;
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function saveAuth(user: AuthUser, token: string) {
  if (!browser) return;
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearAuth() {
  if (!browser) return;
  localStorage.removeItem(USER_STORAGE_KEY);
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function authHeaders() {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

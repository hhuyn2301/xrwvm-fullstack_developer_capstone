import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { api } from './api';
const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState('');
  const [sessionError, setSessionError] = useState('');
  const refreshSession = useCallback(async () => {
    const data = await api('/session');
    setUser(data.authenticated ? data : null);
    setSessionError('');
    return data;
  }, []);
  useEffect(() => {
    let active = true;
    api('/session')
      .then((data) => { if (active) setUser(data.authenticated ? data : null); })
      .catch((error) => { if (active) setSessionError(error.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
  const login = async (credentials) => {
    await api('/login', { method: 'POST', body: credentials });
    const data = await refreshSession();
    setNotice('Welcome back, ' + data.userName + '. You are now logged in.');
  };
  const register = async (details) => {
    await api('/register', { method: 'POST', body: details });
    const data = await refreshSession();
    setNotice(data.authenticated ? 'Your account has been created. Welcome, ' + data.userName + '.' : 'Your account has been created. Please log in.');
    return data.authenticated;
  };
  const logout = async () => {
    await api('/logout', { method: 'POST' });
    setUser(null);
    setNotice('You have been successfully logged out.');
  };
  return <AuthContext.Provider value={{ user, loading, login, register, logout, notice, setNotice, sessionError }}>{children}</AuthContext.Provider>;
}
export const useAuth = () => useContext(AuthContext);

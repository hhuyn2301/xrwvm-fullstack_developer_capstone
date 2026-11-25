import React, { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../AuthContext';
export default function Login() {
  const { user, login, loading } = useAuth();
  const [form, setForm] = useState({ userName: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  if (!loading && user) return <Navigate to="/" replace />;
  const submit = async (event) => {
    event.preventDefault(); setBusy(true); setError('');
    try { await login(form); navigate(location.state?.from || '/'); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  };
  return <section className="auth-layout">
    <div className="auth-intro"><p className="eyebrow">YOUR NEXT CAR STARTS HERE</p><h1>Welcome back.</h1><p>Log in to share your dealership experience and help other drivers choose with confidence.</p><div className="intro-rule" /><p className="muted">Explore dealers. Read reviews. Tell your story.</p></div>
    <form className="panel auth-card" onSubmit={submit}><h2>Login</h2><p className="muted">Use your Best Cars account.</p>
      {error && <div role="alert" className="alert alert-error">{error}</div>}
      <label htmlFor="login-username">Username</label><input id="login-username" name="username" autoComplete="username" required value={form.userName} onChange={(e) => setForm({ ...form, userName: e.target.value })} />
      <label htmlFor="login-password">Password</label><input id="login-password" name="password" type="password" autoComplete="current-password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
      <button className="button full-width" type="submit" disabled={busy}>{busy ? 'Logging in…' : 'Login'}</button>
      <p className="form-footnote">New here? <Link to="/register">Create an account</Link></p>
    </form></section>;
}

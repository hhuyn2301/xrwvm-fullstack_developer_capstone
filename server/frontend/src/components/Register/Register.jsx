import React, { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../../AuthContext';
export default function Register() {
  const { user, register, loading } = useAuth();
  const [form, setForm] = useState({ firstName: '', lastName: '', userName: '', email: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  if (!loading && user) return <Navigate to="/" replace />;
  const change = (event) => setForm({ ...form, [event.target.name]: event.target.value });
  const submit = async (event) => {
    event.preventDefault(); setError('');
    if (form.password !== form.confirmPassword) { setError('Passwords do not match.'); return; }
    setBusy(true);
    const { confirmPassword, ...details } = form;
    try { const authenticated = await register(details); navigate(authenticated ? '/' : '/login'); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  };
  return <section className="auth-layout">
    <div className="auth-intro"><p className="eyebrow">JOIN THE CONVERSATION</p><h1>Your experience<br />can help someone.</h1><p>Create an account to review a dealership, share your purchase details and contribute to better car-buying decisions.</p></div>
    <form className="panel auth-card" onSubmit={submit}><h2>Sign up</h2><p className="muted">Create your Best Cars account.</p>
      {error && <div role="alert" className="alert alert-error">{error}</div>}
      <div className="form-grid"><div><label htmlFor="firstName">First name</label><input id="firstName" name="firstName" autoComplete="given-name" maxLength="150" required value={form.firstName} onChange={change} /></div><div><label htmlFor="lastName">Last name</label><input id="lastName" name="lastName" autoComplete="family-name" maxLength="150" required value={form.lastName} onChange={change} /></div></div>
      <label htmlFor="userName">Username</label><input id="userName" name="userName" autoComplete="username" maxLength="150" required value={form.userName} onChange={change} />
      <label htmlFor="email">Email</label><input id="email" name="email" type="email" autoComplete="email" required value={form.email} onChange={change} />
      <label htmlFor="password">Password</label><input id="password" name="password" type="password" autoComplete="new-password" minLength="8" required value={form.password} onChange={change} /><small className="field-help">Use at least 8 characters and avoid a common password.</small>
      <label htmlFor="confirmPassword">Confirm password</label><input id="confirmPassword" name="confirmPassword" type="password" autoComplete="new-password" required value={form.confirmPassword} onChange={change} />
      <button className="button full-width" type="submit" disabled={busy}>{busy ? 'Creating account…' : 'Create account'}</button>
      <p className="form-footnote">Already registered? <Link to="/login">Login</Link></p>
    </form></section>;
}

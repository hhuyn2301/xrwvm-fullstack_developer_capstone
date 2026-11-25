import React, { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../AuthContext';
export default function Header() {
  const { user, loading, logout, setNotice } = useAuth();
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const onLogout = async () => {
    setBusy(true);
    try { await logout(); navigate('/'); }
    catch (error) { setNotice(error.message); }
    finally { setBusy(false); }
  };
  return <header className="site-header"><a className="skip-link" href="#main-content">Skip to content</a><div className="container header-inner">
    <Link className="brand" to="/" aria-label="Best Cars home"><span className="brand-mark">BC</span><span>Best Cars<small>DEALERSHIP REVIEWS</small></span></Link>
    <nav aria-label="Main navigation"><NavLink to="/" end>Home</NavLink><NavLink to="/about">About Us</NavLink><NavLink to="/contact">Contact Us</NavLink></nav>
    <div className="account-nav">{loading ? <span>Checking account…</span> : user ? <>
      <span className="user-badge"><span className="user-dot" />{user.userName}</span>
      <button className="button button-light button-small" onClick={onLogout} disabled={busy}>{busy ? 'Logging out…' : 'Logout'}</button>
    </> : <><Link className="login-link" to="/login">Login</Link><Link className="button button-small" to="/register">Sign up</Link></>}</div>
  </div></header>;
}

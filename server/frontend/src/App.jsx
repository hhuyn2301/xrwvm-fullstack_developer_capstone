import React, { useEffect } from 'react';
import { Link, Route, Routes, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import Header from './components/Header/Header';
import Login from './components/Login/Login';
import Register from './components/Register/Register';
import Dealers from './components/Dealers/Dealers';
import Dealer from './components/Dealers/Dealer';
import PostReview from './components/Dealers/PostReview';
import { About, Contact } from './components/StaticPages';
function Layout() {
  const { notice, setNotice, sessionError } = useAuth();
  const location = useLocation();
  useEffect(() => { window.scrollTo(0, 0); }, [location.pathname]);
  return <><Header />
    <main id="main-content" className="container main-content">
      {notice && <div role="alert" className="alert alert-success"><span>{notice}</span><button aria-label="Dismiss message" onClick={() => setNotice('')}>×</button></div>}
      {sessionError && <div role="alert" className="alert alert-error">{sessionError}</div>}
      <Routes>
        <Route path="/" element={<Dealers />} /><Route path="/dealers" element={<Dealers />} />
        <Route path="/login" element={<Login />} /><Route path="/register" element={<Register />} /><Route path="/signup" element={<Register />} />
        <Route path="/dealer/:id" element={<Dealer />} /><Route path="/postreview/:id" element={<PostReview />} />
        <Route path="/about" element={<About />} /><Route path="/contact" element={<Contact />} />
        <Route path="*" element={<section className="panel"><h1>Page not found</h1><Link className="button" to="/">View dealerships</Link></section>} />
      </Routes>
    </main>
    <footer className="site-footer"><div className="container"><span className="footer-brand">Best Cars</span><span>Real experiences. Informed decisions.</span><div><Link to="/about">About Us</Link><Link to="/contact">Contact Us</Link></div></div></footer>
  </>;
}
export default function App() { return <AuthProvider><Layout /></AuthProvider>; }

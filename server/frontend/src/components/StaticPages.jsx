import React from 'react';
import { Link } from 'react-router-dom';
export function About() {
  return <><section className="page-hero"><p className="eyebrow">GET TO KNOW BEST CARS</p><h1>About Us</h1><p>We connect car buyers with dealerships and the experiences of the people who have visited them.</p></section>
    <section className="about-story panel"><img src="/static/images/car_dealership.jpg" alt="Cars displayed at a dealership" /><div><h2>A clearer view of your next dealership.</h2><p>Choosing a car is a big decision. Choosing where to buy it matters too. Best Cars brings dealership information and customer reviews together in one place.</p><p>Browse dealers across the United States, filter by state, and read about buying and service experiences before you visit.</p><Link className="button" to="/">Explore dealerships</Link></div></section>
    <section className="value-grid"><article className="panel"><span className="value-number">01</span><h3>Discover</h3><p>Find dealerships by location and explore their details.</p></article><article className="panel"><span className="value-number">02</span><h3>Learn</h3><p>Read customer experiences to make a more informed choice.</p></article><article className="panel"><span className="value-number">03</span><h3>Contribute</h3><p>Share a review and help the next driver on their journey.</p></article></section>
  </>;
}
export function Contact() {
  return <><section className="page-hero"><p className="eyebrow">WE ARE HERE TO HELP</p><h1>Contact Us</h1><p>Have a question about a dealership listing, your account or a review? Find the right contact below.</p></section><section className="contact-layout">
    <div className="panel contact-card"><h2>Customer support</h2><p className="muted">Questions about using Best Cars</p><dl><dt>Email</dt><dd>support@bestcars.example</dd><dt>Hours</dt><dd>Monday–Friday, 9:00 AM–5:00 PM</dd><dt>Account and review help</dt><dd>Include the dealership name and a short description of your question. Never share your password.</dd></dl><p className="demo-note">Course demonstration website. This example email address does not receive messages.</p></div>
    <div className="contact-aside"><h2>Looking for a dealership?</h2><p>Visit the directory to find dealer addresses, customer reviews and state information.</p><Link className="button" to="/">Browse dealerships</Link><div className="contact-divider" /><h3>Want to share feedback?</h3><p>Log in, select a dealership and choose <strong>Post Review</strong> to share your experience.</p><Link className="text-action" to="/login">Login to your account →</Link></div>
  </section></>;
}

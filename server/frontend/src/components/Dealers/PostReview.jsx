import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../../api';
import { useAuth } from '../../AuthContext';
export default function PostReview() {
  const { id } = useParams();
  const { user, loading: authLoading, setNotice } = useAuth();
  const navigate = useNavigate();
  const [dealer, setDealer] = useState(null);
  const [cars, setCars] = useState([]);
  const [form, setForm] = useState({ review: '', purchase: true, purchase_date: '', car_make: '', car_model: '', car_year: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let active = true;
    Promise.all([api('/dealer/' + id), api('/get_cars')]).then(([details, inventory]) => { if (active) {
      setDealer(Array.isArray(details.dealer) ? details.dealer[0] : details.dealer); setCars(inventory.cars || []);
    } }).catch((err) => { if (active) setError(err.message); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [id]);
  const makes = useMemo(() => [...new Set(cars.map((car) => car.car_make))].sort(), [cars]);
  const models = useMemo(() => [...new Set(cars.filter((car) => car.car_make === form.car_make).map((car) => car.name))].sort(), [cars, form.car_make]);
  const years = useMemo(() => [...new Set(cars.filter((car) => car.car_make === form.car_make && car.name === form.car_model).map((car) => car.year))].sort((a, b) => b - a), [cars, form.car_make, form.car_model]);
  const change = (event) => {
    const { name, value, type, checked } = event.target;
    setForm((old) => ({ ...old, [name]: type === 'checkbox' ? checked : value, ...(name === 'car_make' ? { car_model: '', car_year: '' } : {}), ...(name === 'car_model' ? { car_year: '' } : {}) }));
  };
  const submit = async (event) => {
    event.preventDefault(); setBusy(true); setError('');
    try {
      await api('/add_review', { method: 'POST', body: { dealership: Number(id), review: form.review.trim(), purchase: form.purchase, purchase_date: form.purchase ? form.purchase_date : '', car_make: form.purchase ? form.car_make : '', car_model: form.purchase ? form.car_model : '', car_year: form.purchase ? Number(form.car_year) : null } });
      setNotice('Your review has been posted. Thank you for sharing your experience.'); navigate('/dealer/' + id);
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  };
  if (authLoading || loading) return <section className="panel"><p>Preparing your review…</p></section>;
  if (!user) return <section className="panel"><h1>Login to post a review</h1><p>Please sign in before sharing your dealership experience.</p><Link className="button" to="/login" state={{ from: '/postreview/' + id }}>Login</Link></section>;
  return <><Link className="back-link" to={'/dealer/' + id}>← Back to dealer reviews</Link><section className="review-form-layout">
    <div><p className="eyebrow">SHARE YOUR EXPERIENCE</p><h1>Post Review</h1><h2>{dealer?.full_name || 'Dealership #' + id}</h2><p className="muted">{dealer?.city}, {dealer?.state}</p><div className="review-author">Posting as <strong>{user.userName}</strong></div><p>Tell other drivers what went well and what could be improved. Include your vehicle details if you made a purchase.</p></div>
    <form className="panel review-form" onSubmit={submit}>
      {error && <div role="alert" className="alert alert-error">{error}</div>}
      <label htmlFor="review">Your review</label><textarea id="review" name="review" rows="5" minLength="5" maxLength="4000" placeholder="How was your experience at this dealership?" required value={form.review} onChange={change} />
      <label className="checkbox-label" htmlFor="purchase"><input id="purchase" name="purchase" type="checkbox" checked={form.purchase} onChange={change} />I purchased a vehicle from this dealership</label>
      {form.purchase && <fieldset><legend>Purchase details</legend><div className="form-grid">
        <div><label htmlFor="car_make">Car make</label><select id="car_make" name="car_make" value={form.car_make} onChange={change} required><option value="">Select make</option>{makes.map((make) => <option key={make} value={make}>{make}</option>)}</select></div>
        <div><label htmlFor="car_model">Car model</label><select id="car_model" name="car_model" value={form.car_model} onChange={change} disabled={!form.car_make} required><option value="">Select model</option>{models.map((model) => <option key={model} value={model}>{model}</option>)}</select></div>
        <div><label htmlFor="car_year">Model year</label><select id="car_year" name="car_year" value={form.car_year} onChange={change} disabled={!form.car_model} required><option value="">Select year</option>{years.map((year) => <option key={year} value={year}>{year}</option>)}</select></div>
        <div><label htmlFor="purchase_date">Purchase date</label><input id="purchase_date" name="purchase_date" type="date" max={new Date().toISOString().slice(0, 10)} value={form.purchase_date} onChange={change} required /></div>
      </div></fieldset>}
      <div className="form-actions"><Link className="button button-outline" to={'/dealer/' + id}>Cancel</Link><button className="button" type="submit" disabled={busy}>{busy ? 'Posting review…' : 'Submit review'}</button></div>
    </form></section></>;
}

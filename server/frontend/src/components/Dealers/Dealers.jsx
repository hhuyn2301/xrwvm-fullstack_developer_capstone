import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api';
import { useAuth } from '../../AuthContext';
export default function Dealers() {
  const { user } = useAuth();
  const [dealers, setDealers] = useState([]);
  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    setLoading(true); setError('');
    api('/get_dealers' + (selectedState ? '/' + encodeURIComponent(selectedState) : ''))
      .then((data) => {
        if (!active) return;
        const rows = data.dealers || [];
        setDealers(rows);
        if (!selectedState) setStates([...new Set(rows.map((d) => d.state))].sort());
      }).catch((err) => { if (active) setError(err.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [selectedState]);
  const displayed = useMemo(() => dealers.filter((dealer) => [dealer.full_name, dealer.city, dealer.state].some((value) => String(value).toLowerCase().includes(search.trim().toLowerCase()))), [dealers, search]);
  return <><section className="hero"><div><p className="eyebrow">FIND YOUR NEXT DEALERSHIP</p><h1>A better car journey<br />starts with a good dealer.</h1><p>Browse dealerships, learn from customer experiences and share a review of your own.</p><div className="hero-chips"><span>Browse by state</span><span>Read customer reviews</span><span>Share your experience</span></div></div><img src="/static/images/car_dealership.jpg" alt="Car dealership showroom" /></section>
    <section className="directory"><div className="section-heading"><div><p className="eyebrow">THE DIRECTORY</p><h2>Our dealerships</h2></div><p className="muted">{user ? 'Select a dealer to read or post a review.' : <><Link to="/login">Login</Link> to post a review.</>}</p></div>
      <div className="filters panel"><div className="search-field"><label htmlFor="dealer-search">Search dealerships</label><input id="dealer-search" type="search" placeholder="Dealer name, city or state" value={search} onChange={(e) => setSearch(e.target.value)} /></div><div className="state-field"><label htmlFor="state-filter">Filter by state</label><select id="state-filter" value={selectedState} onChange={(e) => setSelectedState(e.target.value)}><option value="">All states</option>{states.map((state) => <option key={state} value={state}>{state}</option>)}</select></div><span className="result-count" aria-live="polite">{loading ? 'Loading…' : displayed.length + ' dealerships'}</span></div>
      {error && <div role="alert" className="alert alert-error">{error}</div>}
      <div className="table-wrap panel"><table><thead><tr><th scope="col">ID</th><th scope="col">Dealership</th><th scope="col">City</th><th scope="col">State</th><th scope="col">Address</th><th scope="col">Reviews</th>{user && <th scope="col">Your experience</th>}</tr></thead>
        <tbody>{loading ? <tr><td colSpan={user ? 7 : 6}>Loading dealerships…</td></tr> : displayed.length === 0 ? <tr><td colSpan={user ? 7 : 6}>No dealerships match your selection.</td></tr> : displayed.map((dealer) => <tr key={dealer.id}>
          <td className="table-id">{dealer.id}</td><td><Link className="dealer-name" to={'/dealer/' + dealer.id}>{dealer.full_name}</Link></td><td>{dealer.city}</td><td>{dealer.state}</td><td>{dealer.address}<small className="postal-code">{dealer.zip}</small></td><td><Link className="text-action" to={'/dealer/' + dealer.id}>View reviews →</Link></td>{user && <td><Link className="button button-outline button-small" to={'/postreview/' + dealer.id}>Post Review</Link></td>}
        </tr>)}</tbody></table></div>
    </section></>;
}

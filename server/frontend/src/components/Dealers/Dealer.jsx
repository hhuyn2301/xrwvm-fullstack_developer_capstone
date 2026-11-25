import React, { useEffect, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { api } from '../../api';
import { useAuth } from '../../AuthContext';
export default function Dealer() {
  const { id } = useParams();
  const { user } = useAuth();
  const location = useLocation();
  const [dealer, setDealer] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    setLoading(true); setError('');
    Promise.all([api('/dealer/' + id), api('/reviews/dealer/' + id)])
      .then(([details, response]) => { if (active) { setDealer(Array.isArray(details.dealer) ? details.dealer[0] : details.dealer); setReviews(response.reviews || []); } })
      .catch((err) => { if (active) setError(err.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [id, location.key]);
  if (loading) return <section className="panel"><p>Loading dealer details and reviews…</p></section>;
  if (error) return <div role="alert" className="alert alert-error">{error}</div>;
  if (!dealer) return <section className="panel"><h1>Dealer not found</h1><Link to="/">Back to dealerships</Link></section>;
  return <><Link className="back-link" to="/">← All dealerships</Link>
    <section className="dealer-heading panel"><div><p className="eyebrow">DEALERSHIP #{dealer.id}</p><h1>{dealer.full_name}</h1><p>{dealer.address}, {dealer.city}, {dealer.state} {dealer.zip}</p><span className="location-pill">{dealer.state}</span></div>{user ? <Link className="button" to={'/postreview/' + id}>Post Review</Link> : <Link className="button button-outline" to="/login" state={{ from: '/postreview/' + id }}>Login to post a review</Link>}</section>
    <div className="section-heading"><div><p className="eyebrow">CUSTOMER EXPERIENCES</p><h2>Dealer reviews</h2></div><span className="muted">{reviews.length} {reviews.length === 1 ? 'review' : 'reviews'}</span></div>
    {reviews.length === 0 ? <div className="panel"><h3>Be the first to share your experience.</h3><p>No reviews have been posted for this dealership yet.</p></div> : <div className="review-grid">{[...reviews].sort((a, b) => Number(b.id) - Number(a.id)).map((review) => {
      const sentiment = ['positive', 'negative', 'neutral'].includes(review.sentiment) ? review.sentiment : 'unavailable';
      return <article className="review-card panel" key={review.id || review._id}>
        <div className="review-top"><div className="reviewer-avatar" aria-hidden="true">{(review.name || '?').charAt(0).toUpperCase()}</div><div><h3>{review.name}</h3><small>Customer review #{review.id}</small></div><span className={'sentiment sentiment-' + sentiment}>{sentiment === 'unavailable' ? 'Sentiment unavailable' : sentiment}</span></div>
        <p className="review-text">{review.review}</p>{review.purchase ? <div className="purchase-details"><strong>{[review.car_year, review.car_make, review.car_model].filter(Boolean).join(' ')}</strong><span>Purchased {review.purchase_date}</span></div> : <div className="purchase-details"><span>Dealership visit · no vehicle purchase</span></div>}
      </article>;
    })}</div>}
  </>;
}

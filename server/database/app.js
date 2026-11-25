const express = require('express');
const mongoose = require('mongoose');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const cors = require('cors');

const Reviews = require('./review');
const Dealerships = require('./dealership');
const Counter = mongoose.model('counters', new mongoose.Schema({
  _id: String,
  seq: { type: Number, required: true }
}, { versionKey: false }));

function positiveId(value) {
  const text = String(value);
  if (!/^[1-9][0-9]*$/.test(text)) return null;
  const number = Number(text);
  return Number.isSafeInteger(number) ? number : null;
}

function validateReviewInput(body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    throw new Error('A JSON object is required.');
  }
  const dealership = positiveId(body.dealership);
  if (!dealership) throw new Error('A valid dealership ID is required.');
  const name = typeof body.name === 'string' ? body.name.trim() : '';
  const review = typeof body.review === 'string' ? body.review.trim() : '';
  if (!name || name.length > 100) throw new Error('Name must contain 1–100 characters.');
  if (!review || review.length > 5000) throw new Error('Review must contain 1–5000 characters.');
  if (typeof body.purchase !== 'boolean') throw new Error('Purchase must be true or false.');

  const result = { name, dealership, review, purchase: body.purchase,
    purchase_date: '', car_make: '', car_model: '', car_year: null };
  if (body.purchase) {
    for (const field of ['car_make', 'car_model']) {
      if (typeof body[field] !== 'string' || !body[field].trim() ||
          body[field].trim().length > 100) {
        throw new Error('A valid ' + field + ' is required for a purchase.');
      }
      result[field] = body[field].trim();
    }
    if (typeof body.purchase_date !== 'string' ||
        !/^\d{4}-\d{2}-\d{2}$/.test(body.purchase_date)) {
      throw new Error('Purchase date must use YYYY-MM-DD.');
    }
    const date = new Date(body.purchase_date + 'T00:00:00Z');
    if (Number.isNaN(date.getTime()) ||
        date.toISOString().slice(0, 10) !== body.purchase_date) {
      throw new Error('Purchase date is not a valid calendar date.');
    }
    if (date.getTime() > Date.now()) throw new Error('Purchase date cannot be in the future.');
    const year = Number(body.car_year);
    if (!Number.isInteger(year) || year < 1886 ||
        year > new Date().getUTCFullYear() + 1) {
      throw new Error('A valid car year is required.');
    }
    result.purchase_date = body.purchase_date;
    result.car_year = year;
  }
  return result;
}

function validToken(actual, expected) {
  const a = Buffer.from(actual || '', 'utf8');
  const b = Buffer.from(expected, 'utf8');
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

const asyncRoute = handler => (req, res, next) =>
  Promise.resolve(handler(req, res, next)).catch(next);

function createApp(options = {}) {
  const app = express();
  const writeToken = options.writeToken ?? process.env.WRITE_API_TOKEN ?? '';
  app.disable('x-powered-by');
  app.set('json spaces', 2);
  app.use(cors());
  app.use(express.json({ limit: '64kb' }));

  app.get('/', (_req, res) => res.json({
    service: 'Dealerships and Reviews API',
    endpoints: ['/fetchDealers', '/fetchDealers/Kansas', '/fetchDealer/15',
      '/fetchReviews/dealer/15', '/health']
  }));
  app.get('/health', (_req, res) => {
    const connected = mongoose.connection.readyState === 1;
    res.status(connected ? 200 : 503).json({
      status: connected ? 'ok' : 'unavailable',
      database: connected ? 'connected' : 'disconnected'
    });
  });

  app.get('/fetchDealers', asyncRoute(async (_req, res) => {
    res.json(await Dealerships.find().select('-_id').sort({ id: 1 }).lean());
  }));
  app.get('/fetchDealers/:state', asyncRoute(async (req, res) => {
    const state = req.params.state.trim();
    if (!state || state.length > 60) return res.status(400).json({ error: 'Invalid state.' });
    const escaped = state.replace(/[.*+?^$()|[\]\\]/g, '\\$&');
    res.json(await Dealerships.find({ state: new RegExp('^' + escaped + '$', 'i') })
      .select('-_id').sort({ id: 1 }).lean());
  }));
  app.get('/fetchDealer/:id', asyncRoute(async (req, res) => {
    const id = positiveId(req.params.id);
    if (!id) return res.status(400).json({ error: 'Invalid dealership ID.' });
    const dealer = await Dealerships.findOne({ id }).select('-_id').lean();
    if (!dealer) return res.status(404).json({ error: 'Dealership not found.' });
    res.json(dealer);
  }));
  app.get('/fetchReviews', asyncRoute(async (_req, res) => {
    res.json(await Reviews.find().select('-_id').sort({ id: 1 }).lean());
  }));
  app.get('/fetchReviews/dealer/:id', asyncRoute(async (req, res) => {
    const dealership = positiveId(req.params.id);
    if (!dealership) return res.status(400).json({ error: 'Invalid dealership ID.' });
    const exists = await Dealerships.exists({ id: dealership });
    if (!exists) return res.status(404).json({ error: 'Dealership not found.' });
    res.json(await Reviews.find({ dealership }).select('-_id').sort({ id: 1 }).lean());
  }));
  app.post('/insert_review', asyncRoute(async (req, res) => {
    if (writeToken && !validToken(req.get('X-API-Key'), writeToken)) {
      return res.status(401).json({ error: 'Invalid internal API token.' });
    }
    let data;
    try {
      data = validateReviewInput(req.body);
    } catch (error) {
      return res.status(400).json({ error: error.message });
    }
    if (!await Dealerships.exists({ id: data.dealership })) {
      return res.status(404).json({ error: 'Dealership not found.' });
    }
    const counter = await Counter.findOneAndUpdate(
      { _id: 'review' }, { $inc: { seq: 1 } }, { new: true }
    );
    if (!counter) throw new Error('Review ID counter has not been initialized.');
    const saved = await Reviews.create({ ...data, id: counter.seq });
    const result = saved.toObject();
    delete result._id;
    res.status(201).json(result);
  }));
  app.use((_req, res) => res.status(404).json({ error: 'Endpoint not found.' }));
  app.use((error, _req, res, _next) => {
    if (error.type === 'entity.parse.failed') {
      return res.status(400).json({ error: 'Request body is not valid JSON.' });
    }
    if (error.type === 'entity.too.large') {
      return res.status(413).json({ error: 'Request body is too large.' });
    }
    if (error.name === 'ValidationError') {
      return res.status(400).json({ error: 'Review validation failed.' });
    }
    console.error('API request failed:', error.message);
    res.status(503).json({ error: 'Database request failed. Please try again.' });
  });
  return app;
}

async function seedMissing(model, rows) {
  // Never delete or overwrite existing application data at startup.
  try {
    await model.bulkWrite(rows.map(row => ({
      updateOne: { filter: { id: row.id }, update: { $setOnInsert: row }, upsert: true }
    })), { ordered: false });
  } catch (error) {
    // Concurrent app starts may race on an already-created unique ID.
    if (!error.writeErrors?.length ||
        !error.writeErrors.every(item => item.code === 11000)) throw error;
  }
}

async function initializeDatabase(uri = process.env.MONGODB_URI ||
    'mongodb://127.0.0.1:27017/dealershipsDB') {
  await mongoose.connect(uri, { serverSelectionTimeoutMS: 10000 });
  await Promise.all([Dealerships.init(), Reviews.init(), Counter.init()]);
  const load = file => JSON.parse(fs.readFileSync(path.join(__dirname, 'data', file), 'utf8'));
  await seedMissing(Dealerships, load('dealerships.json').dealerships);
  await seedMissing(Reviews, load('reviews.json').reviews);
  const latest = await Reviews.findOne().sort({ id: -1 }).select('id').lean();
  await Counter.updateOne(
    { _id: 'review' }, { $max: { seq: latest?.id || 0 } }, { upsert: true }
  );
}

async function start() {
  await initializeDatabase();
  const port = Number(process.env.PORT || 3030);
  const server = createApp().listen(port, '0.0.0.0', () => {
    console.log('Dealership API listening on port ' + port + ' (MongoDB connected).');
  });
  async function close() {
    server.close(async () => {
      await mongoose.disconnect();
      process.exit(0);
    });
  }
  process.once('SIGTERM', close);
  process.once('SIGINT', close);
  return server;
}

if (require.main === module) {
  start().catch(error => {
    console.error('Could not start dealership API:', error.message);
    process.exit(1);
  });
}

module.exports = { createApp, validateReviewInput, positiveId, initializeDatabase, start };

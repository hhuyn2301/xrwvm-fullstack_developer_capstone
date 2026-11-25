const test = require('node:test');
const assert = require('node:assert/strict');
const { once } = require('node:events');
const { createApp, positiveId, validateReviewInput } = require('../app');

const base = { name: 'Sample Reviewer', dealership: 15,
  review: 'Helpful staff and a clear explanation.', purchase: false };

test('normalizes a non-purchase review and ignores forged database IDs', () => {
  const data = validateReviewInput({ ...base, id: 7, name: '  Sample Reviewer  ' });
  assert.equal(data.name, 'Sample Reviewer');
  assert.equal(data.car_year, null);
  assert.equal(data.id, undefined);
});
test('validates complete purchase records', () => {
  const data = validateReviewInput({ ...base, purchase: true,
    purchase_date: '2023-09-10', car_make: 'Toyota', car_model: 'Camry', car_year: 2023 });
  assert.equal(data.car_year, 2023);
  assert.equal(data.purchase, true);
});
test('rejects missing text, invalid dates and non-boolean purchase flags', () => {
  assert.throws(() => validateReviewInput({ ...base, review: ' ' }), /Review/);
  assert.throws(() => validateReviewInput({ ...base, purchase: 'false' }), /Purchase/);
  assert.throws(() => validateReviewInput({ ...base, purchase: true,
    purchase_date: '2023-02-30', car_make: 'Toyota', car_model: 'Camry', car_year: 2023 }), /calendar/);
});
test('route IDs cannot contain database operators or exponent notation', () => {
  assert.equal(positiveId('15'), 15);
  for (const value of ['1e2', '-1', '0', '1.5', { $gt: 0 }, '9007199254740992']) {
    assert.equal(positiveId(value), null);
  }
});
test('HTTP malformed JSON and protected writes fail before database access', async () => {
  const server = createApp({ writeToken: 'test-only-token' }).listen(0, '127.0.0.1');
  await once(server, 'listening');
  const baseUrl = 'http://127.0.0.1:' + server.address().port;
  try {
    const malformed = await fetch(baseUrl + '/insert_review', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{oops'
    });
    assert.equal(malformed.status, 400);
    const unauthenticated = await fetch(baseUrl + '/insert_review', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(base)
    });
    assert.equal(unauthenticated.status, 401);
    const invalidId = await fetch(baseUrl + '/fetchDealer/no-id');
    assert.equal(invalidId.status, 400);
  } finally {
    await new Promise(resolve => server.close(resolve));
  }
});

const mongoose = require('mongoose');

const reviewSchema = new mongoose.Schema({
  id: { type: Number, required: true, unique: true },
  name: { type: String, required: true, maxlength: 100 },
  dealership: { type: Number, required: true, index: true },
  review: { type: String, required: true, maxlength: 5000 },
  purchase: { type: Boolean, required: true },
  purchase_date: { type: String, default: '' },
  car_make: { type: String, default: '' },
  car_model: { type: String, default: '' },
  car_year: { type: Number, default: null }
}, { versionKey: false, timestamps: true });

module.exports = mongoose.model('reviews', reviewSchema);

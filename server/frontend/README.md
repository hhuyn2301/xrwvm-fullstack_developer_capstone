# Best Cars React frontend

Completed user interface for the IBM dealership capstone.
Requires Node.js 22.12+ (Node 24 supported).

Run npm ci, then npm run build.
Output: build/index.html and build/static/react/ hashed assets.
Django must serve the UI routes and collect build/static/ and public/static/.
Run npm start for Vite development; API routes proxy to Django at port 8000.

Features: Django session/CSRF authentication, registration, logout alert,
dealership directory/state filtering, details/reviews, review creation with
car make/model/year and purchase details, About Us and Contact Us.

No mock dealer data or simulated successful authentication is used.
The Contact Us page uses an explicitly labeled example email address.

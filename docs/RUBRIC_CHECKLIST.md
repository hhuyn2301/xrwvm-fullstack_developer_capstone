# Best Cars: Full-Stack Dealership Review Platform

## Submission checklist — 28 tasks, 50 points

Submit your own public fork URL, your actual deployment URL, and 26 genuine screenshots.
Keep the browser address bar visible whenever the rubric requires an endpoint. Local
previews demonstrate features; GitHub and deployment evidence require actual remote runs.
Replace the base URL with the real local/lab/deployment URL shown by your environment.

| Task | Points | Submitted item | Required visible content |
|---|---:|---|---|
| 1 | 1 | Public GitHub fork URL | Your repository with all completed code changes. |
| 2 | 1 | django_server.png | Actual terminal running python manage.py runserver, successful checks and server address. Capture in Static Pages lab. |
| 3 | 3 | about_us.png | Working About Us page at /about in the Django application. |
| 4 | 2 | contact_us.png | Working Contact Us page at /contact. |
| 5 | 2 | login.png | Home/dealers page after login, showing the logged-in username. |
| 6 | 2 | logout.png | The logout alert, captured before dismissing it. |
| 7 | 1 | sign-up.png | Registration page at /register with its input fields. |
| 8 | 2 | dealer_review.png | Express /fetchReviews/dealer/15, actual reviews and address bar. |
| 9 | 2 | dealerships.png | Express /fetchDealers, dealer JSON and address bar. |
| 10 | 2 | dealer_details.png | Express /fetchDealer/15, full selected dealer details and address bar. |
| 11 | 2 | kansasDealers.png | Express /fetchDealers/Kansas, Kansas-only dealer JSON and address bar. |
| 12 | 2 | admin_login.png | Django /admin/ after login as your real root/superuser. |
| 13 | 1 | admin_logout.png | Django admin logged-out confirmation. |
| 14 | 2 | cars.png | Populated Car Makes at /admin/djangoapp/carmake/ and address bar. |
| 15 | 2 | car_models.png | Populated Car Models at /admin/djangoapp/carmodel/. |
| 16 | 2 | sentiment_analyzer.png | Deployed sentiment service /analyze/<text> response and deployed URL in address bar. |
| 17 | 1 | get_dealers.png | Home/dealers page before login and address bar. |
| 18 | 2 | get_dealers_loggedin.png | Home/dealers page after login, username, Post Review buttons and address bar. |
| 19 | 2 | dealersbystate.png | State-filtered dealers, selected State and address bar. |
| 20 | 1 | dealer_id_reviews.png | /dealer/15 showing dealer details and reviews, with address bar. |
| 21 | 1 | dealership_review_submission.png | Filled Post Review form BEFORE submission, review text and purchase/car details, with address bar. |
| 22 | 2 | added_review.png | Newly saved review matching Task 21's inputs, with address bar. |
| 23 | 3 | CICD.png | Successful actual GitHub Actions run in your fork, showing workflow, commit and green jobs. |
| 24 | 1 | Deployment URL | Actual base URL of deployed Django app; must agree with Tasks 25–28. |
| 25 | 2 | deployed_landingpage.png | Deployed landing page and address bar using the Task 24 origin. |
| 26 | 2 | deployed_loggedin.png | Deployed app after login, username and address bar using the Task 24 origin. |
| 27 | 2 | deployed_dealer_detail.png | Deployed dealer details/reviews and address bar using the Task 24 origin. |
| 28 | 2 | deployed_add_review.png | Review actually added through deployed app and address bar using the Task 24 origin. |

The rubric also accepts .jpg. Use one clear screenshot per field. Task 24's base origin
must match Tasks 25–28; individual page paths can differ. Dealer 15 has reviews in the
supplied course data. A Kansas example is dealer 8, Bytecard Car Dealership, Topeka.

## Capture sequence

1. Start services, seed car data, and create your admin account. Capture Task 2 in the
   actual lab terminal while the Django development server is running.
2. Capture About, Contact, Sign-up and the logged-out dealer list.
3. Open the four Express endpoints in a browser, one at a time.
4. Log in to Django admin, capture makes/models, then log out and capture confirmation.
5. Register/login through React. Capture username, Post Review button, state filter and
   dealer details.
6. Fill a review form and capture it before submission. Submit once, then capture the
   same review on the dealer page. Capture the logout alert before dismissing it.
7. Push code to your own fork. Wait for a real CI success and capture GitHub Actions.
8. Deploy sentiment and the full app in the course environment. Capture the deployed
   service and four deployed app views using the same deployment origin.

Code and workflow definitions alone are not evidence of successful GitHub/cloud runs.
Populate the two submitted URLs only after those resources exist. Take each screenshot
from the actual runtime indicated by the assignment.

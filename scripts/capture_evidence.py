"""Capture genuine local browser windows for rubric review.
Run under xvfb-run on a Linux host with the full stack already running.
This script never represents localhost screenshots as IBM cloud deployment.
"""
from pathlib import Path
import argparse
import json
import os
import secrets
import subprocess
import tempfile
import time
import urllib.request
from urllib.parse import urlsplit
from PIL import ImageGrab
from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser()
parser.add_argument("--base-url", default="http://127.0.0.1:8000")
parser.add_argument("--api-url", default="http://127.0.0.1:3030")
parser.add_argument("--sentiment-url", default="http://127.0.0.1:5050")
parser.add_argument("--output", default="screenshots/local")
parser.add_argument("--server-log", default="evidence/django-server.log")
args = parser.parse_args()
for url in (args.base_url, args.api_url, args.sentiment_url):
    if urlsplit(url).hostname not in {"127.0.0.1", "localhost"}:
        raise SystemExit("This local evidence script accepts localhost only.")
if not os.getenv("DISPLAY"):
    raise SystemExit("Run with xvfb-run -a -s '-screen 0 1440x1200x24'.")
admin_password = os.environ["CAPTURE_ADMIN_PASSWORD"]
user_password = secrets.token_urlsafe(20)
env = os.environ.copy()
OUT = Path(args.output).resolve()
OUT.mkdir(parents=True, exist_ok=True)
RUNTIME = Path(tempfile.mkdtemp(prefix="dealership-capture-"))
captures = []

def wait_http(url, limit=90):
    deadline = time.monotonic() + limit
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("Service did not become ready: " + url)

def capture(name, page=None, note=""):
    time.sleep(0.5)
    ImageGrab.grab(xdisplay=os.environ["DISPLAY"]).save(OUT / name)
    captures.append({
        "file": name,
        "url": page.url if page else None,
        "scope": "local execution, not IBM cloud deployment",
        "note": note,
    })
    print("Captured", name, flush=True)

for url in (args.base_url, args.api_url, args.sentiment_url):
    wait_http(url.rstrip("/") + "/health")

terminal = None
try:
    log = Path(args.server_log).resolve()
    if log.is_file():
        terminal = subprocess.Popen([
            "xterm", "-geometry", "130x45+0+0", "-fa", "DejaVu Sans Mono",
            "-fs", "12", "-title", "Django development server",
            "-e", "tail", "-n", "35", "-f", str(log),
        ], env=env)
        time.sleep(2)
        capture("django_server.png", note="Actual Django runserver log while server is running.")
        terminal.terminate()
        terminal.wait(timeout=10)
        terminal = None
    with sync_playwright() as p:
     context=p.chromium.launch_persistent_context(
      str(RUNTIME/'browser-profile'),
      headless=False,no_viewport=True,env=env,
      args=['--no-sandbox','--disable-dev-shm-usage','--window-size=1440,1200',
            '--window-position=0,0','--no-first-run','--disable-session-crashed-bubble'],
     )
     page=context.pages[0]
     page.set_default_timeout(20000)
     errors=[]
     page.on('pageerror',lambda error: errors.append(str(error)))
     base=args.base_url.rstrip('/')
     def goto(path):
      page.goto(base+path,wait_until='networkidle')
     goto('/about')
     page.get_by_role('heading',name='About Us',exact=True).wait_for()
     capture('about_us.png',page)
     goto('/contact')
     page.get_by_role('heading',name='Contact Us',exact=True).wait_for()
     capture('contact_us.png',page)
     goto('/')
     page.locator('tbody .dealer-name').first.wait_for()
     assert page.get_by_role('link',name='Post Review',exact=True).count()==0
     capture('get_dealers.png',page)
     goto('/register')
     page.get_by_role('heading',name='Sign up',exact=True).wait_for()
     capture('sign-up.png',page)
     username='huyen_demo_'+secrets.token_hex(2)
     for label,value in [
      ('First name','Demo'),('Last name','Learner'),('Username',username),
      ('Email','learner@example.test'),('Password',user_password),
      ('Confirm password',user_password),
     ]: page.get_by_label(label,exact=True).fill(value)
     page.get_by_role('button',name='Create account',exact=True).click()
     page.locator('.user-badge').wait_for()
     assert username in page.locator('.user-badge').inner_text()
     page.get_by_role('button',name='Logout',exact=True).click()
     page.get_by_role('alert').filter(has_text='You have been successfully logged out.').wait_for()
     capture('logout.png',page)
     goto('/login')
     page.get_by_label('Username',exact=True).fill(username)
     page.get_by_label('Password',exact=True).fill(user_password)
     page.get_by_role('button',name='Login',exact=True).click()
     page.locator('.user-badge').wait_for()
     page.get_by_role('link',name='Post Review',exact=True).first.wait_for()
     capture('login.png',page)
     capture('get_dealers_loggedin.png',page)
     page.get_by_label('Filter by state',exact=True).select_option('Kansas')
     page.get_by_role('link',name='Bytecard Car Dealership',exact=True).wait_for()
     expect(page.locator('tbody tr')).to_have_count(1)
     capture('dealersbystate.png',page)
     goto('/dealer/15')
     page.get_by_role('heading',name='Tempsoft Car Dealership',exact=True).wait_for()
     page.locator('.review-card').first.wait_for()
     capture('dealer_id_reviews.png',page)
     goto('/postreview/15')
     review='The staff were helpful and explained the car clearly. The purchase process was smooth, and I would recommend this dealership.'
     page.get_by_label('Your review',exact=True).fill(review)
     page.get_by_label('Car make',exact=True).select_option('Toyota')
     page.get_by_label('Car model',exact=True).select_option('Camry')
     page.get_by_label('Model year',exact=True).select_option('2023')
     page.get_by_label('Purchase date',exact=True).fill('2023-11-20')
     capture('dealership_review_submission.png',page)
     page.get_by_role('button',name='Submit review',exact=True).click()
     page.locator('.review-card').filter(has_text=review).wait_for()
     assert '2023 Toyota Camry' in page.locator('.review-card').filter(has_text=review).inner_text()
     capture('added_review.png',page)

     for path,filename in [
      (args.api_url.rstrip('/')+'/fetchReviews/dealer/15','dealer_review.png'),
      (args.api_url.rstrip('/')+'/fetchDealers','dealerships.png'),
      (args.api_url.rstrip('/')+'/fetchDealer/15','dealer_details.png'),
      (args.api_url.rstrip('/')+'/fetchDealers/Kansas','kansasDealers.png'),
     ]:
      page.goto(path,wait_until='networkidle')
      capture(filename,page)

     goto('/admin/')
     page.get_by_label('Username:',exact=True).fill('root')
     page.get_by_label('Password:',exact=True).fill(admin_password)
     page.get_by_role('button',name='Log in',exact=True).click()
     page.get_by_text('Car catalogue and user management',exact=True).wait_for()
     capture('admin_login.png',page)
     goto('/admin/djangoapp/carmake/')
     page.get_by_text('Select car make to change',exact=True).wait_for()
     capture('cars.png',page)
     goto('/admin/djangoapp/carmodel/')
     page.get_by_text('Select car model to change',exact=True).wait_for()
     capture('car_models.png',page)
     page.get_by_role('button',name='Log out',exact=True).click()
     page.get_by_text('Logged out',exact=True).wait_for()
     capture('admin_logout.png',page)
     page.goto(args.sentiment_url.rstrip('/')+'/analyze/This%20dealership%20was%20excellent',wait_until='networkidle')
     capture('sentiment_analyzer_LOCAL_ONLY.png',page,note='Local sentiment reference only; Task 16 requires a deployed URL.')
     (OUT/'capture_manifest.json').write_text(json.dumps({
      'scope':'Local validation screenshots from actual services, not Skills Network lab or cloud deployment evidence.',
      'capture_method':'Unmodified X11 desktop captures with a real headed Chromium address bar.',
      'screenshots':captures,'browser_errors':errors,
      'review_before_after':{'dealer_id':15,'username':username,'text':review,'car':'2023 Toyota Camry','purchase_date':'2023-11-20'},
      'cloud_evidence_not_captured':[16,24,25,26,27,28],
     },ensure_ascii=False,indent=2))
     context.close()
     assert not errors,errors
    print("Captured genuine local evidence:", len(captures), "images.", flush=True)
finally:
    if terminal and terminal.poll() is None:
        terminal.terminate()

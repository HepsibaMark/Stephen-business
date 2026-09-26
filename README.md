# Grocery Delivery App — Full Project

This ZIP contains BOTH parts of the app:

```
grocery-delivery-app/
├── backend/    ← FastAPI server (products, orders, login)
└── frontend/   ← React website (catalog, cart, checkout)
```

Delete all your old folders/zips from before — this replaces
everything. Start fresh from this one.

---

## One-time setup

### 1. Backend

Open a terminal and run these one at a time:

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Then open the new `.env` file in Notepad and set:
```
DATABASE_URL=sqlite:///./test.db
```
(leave the other lines as they are for now)

Save and close it, then start the server:
```
uvicorn app.main:app --reload
```

Leave this terminal running. You should see "Application startup
complete."

### 2. Load the real product catalog (one time only)

Open a SECOND terminal:
```
cd backend
venv\Scripts\activate
python load_catalog.py
```
You should see 72 checkmarks print.

### 3. Frontend

Open a THIRD terminal:
```
cd frontend
npm install
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## Using it

- First time: enter any email address on the login screen, click
  "Send OTP" — the code appears right on screen (test mode, no real
  email sent yet — see backend/app/auth.py if you want to turn on
  real email sending later, it's free using your own Gmail).
- Browse the catalog, add items to your cart, enter a delivery
  address, and checkout — a real order gets saved.

## If something breaks

- **Backend won't start**: make sure you're inside the `backend`
  folder and `venv` is activated (you'll see `(venv)` in your prompt).
- **Frontend shows no products**: make sure the backend terminal
  is still running, and that you ran `load_catalog.py`.
- **"Module not found" errors**: run `pip install -r requirements.txt`
  again inside the backend folder with venv activated.

## What's built so far

- Product catalog (72 real items, bilingual names, correct
  kg/piece/kattu units)
- Cart + checkout, saved as real orders
- Email OTP login (test mode — free, no signup needed)

## What's NOT built yet

- Admin panel (see orders / manage stock — currently only via
  backend's /docs technical page)
- Real payment (currently defaults to Cash on Delivery)
- Deployment (currently only runs on your own laptop)

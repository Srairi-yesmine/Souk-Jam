# Souk'Jam Frontend

This frontend is a lightweight React application (Vite) that connects to the Souk'Jam API running at `http://localhost:5000`.

## Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Start the frontend development server:

```bash
npm run dev
```

3. The frontend will be available at `http://localhost:3000` and API requests are proxied to `http://localhost:5000`.

## Notes
- Add the `2.png` logo to `src/assets/2.png` if you want the app to display the logo.
- The frontend uses `localStorage` to store `access_token` and `user_id` after login.
- The proxy in `vite.config.js` rewrites `/api` to the backend; the frontend currently calls the backend directly at `http://localhost:5000` in `src/api.js`.

# Vercel deployment for Bizora frontend

## 1) Import the project

- Open https://vercel.com
- Import the `frontend` folder as a new project
- Set the project root to `frontend`

## 2) Framework preset

Use:
- Framework: Next.js
- Root directory: `frontend`

## 3) Environment variables

Add this in Vercel project settings:

- `NEXT_PUBLIC_API_URL` = `https://your-backend-domain.com`

## 4) Build settings

Vercel should detect Next.js automatically. The repo already includes:

- `frontend/vercel.json`
- `frontend/next.config.mjs`

## 5) Deployment URL

After deployment, Vercel will give you something like:

- `https://bizora-frontend.vercel.app`

Then set the backend `ALLOWED_ORIGINS` to include that domain.

## 6) Backend CORS

In the backend deployment environment, set:

- `ALLOWED_ORIGINS=https://your-vercel-app.vercel.app`

## 7) Final API connection

The frontend uses `NEXT_PUBLIC_API_URL` to reach the FastAPI backend.

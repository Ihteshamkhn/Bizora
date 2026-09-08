# Bizora Deployment Guide

This project is prepared for a production deployment setup with a separate frontend, backend, and PostgreSQL database.

## Recommended architecture

- Frontend: Next.js app hosted on Vercel, Netlify, or another Node host
- Backend: FastAPI hosted on Render, Railway, Azure App Service, or any Python host
- Database: PostgreSQL on Neon, Supabase, Railway, or Azure Database

## Required environment variables

### Backend

Copy [backend/.env.production.example](backend/.env.production.example) to a real env file or set these in your hosting platform:

- DATABASE_URL
- JWT_SECRET
- GROQ_API_KEY
- GROQ_MODEL
- DEBUG=false
- ALLOWED_ORIGINS

### Frontend

Copy [frontend/.env.production.example](frontend/.env.production.example) and replace the backend URL with your deployed FastAPI URL.

- NEXT_PUBLIC_API_URL=https://your-backend-domain.com

## Production build verification

The project has already been validated with:

- backend compile check
- frontend production build

## Local deployment-style run

### Backend

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

### Frontend

```bash
cd frontend
npm install
npm run build
npm run start
```

## Container deployment

Docker files are included for both services:

- [backend/Dockerfile](backend/Dockerfile)
- [frontend/Dockerfile](frontend/Dockerfile)

## Important production notes

- Use a real PostgreSQL database, not SQLite for production
- Set a strong JWT secret in your hosting platform
- Add your frontend domain to ALLOWED_ORIGINS
- Set the backend API URL in the frontend environment variables
- Use HTTPS only in production

## Health checks

- Frontend: http://localhost:3000
- Backend: http://localhost:8000/health
- API docs: http://localhost:8000/docs

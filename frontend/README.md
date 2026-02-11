# SaaS Booking Frontend

Next.js 14 frontend for the SaaS Booking Backend.

## Stack

- Next.js 14 (App Router)
- TypeScript
- TailwindCSS
- No heavy UI libraries

## Setup

```bash
cd frontend
npm install
```

## Environment

Create `.env.local` (already included):

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

The `next.config.js` proxies `/api/*` requests to the backend URL, so the frontend and backend can run on different ports without CORS issues.

## Run

```bash
# Make sure the backend is running on port 8000 first
npm run dev
```

Frontend will be available at `http://localhost:3000`.

## Pages

| Route | Description |
|---|---|
| `/login` | Login / Register |
| `/dashboard` | Business selection |
| `/dashboard/staff` | Staff CRUD |
| `/dashboard/services` | Services CRUD |
| `/dashboard/customers` | Customers CRUD |
| `/dashboard/bookings` | Bookings list + cancel |
| `/dashboard/calendar` | Select staff + date, view slots, create booking |

## How it works

1. User logs in or registers at `/login`
2. JWT token is stored in `localStorage`
3. User selects a business at `/dashboard`
4. Business ID is stored in `localStorage`
5. All API calls attach `Authorization: Bearer <token>` and `X-Business-ID: <id>` headers automatically
6. Sidebar navigation provides access to all CRUD pages and calendar

# Frontend - Next.js Face Recognition UI

Modern, responsive web interface for face recognition.

## Quick Start

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Open http://localhost:3000

## Features

- Real-time webcam preview
- Capture and recognize faces
- Register new people
- View all registered people
- Delete people from database
- Display confidence scores and metrics
- Responsive design

## Configuration

### API URL

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Components

- `app/page.tsx` - Main application page
- `lib/api.ts` - API client functions
- `app/globals.css` - Global styles
- `app/page.module.css` - Component styles

## Build for Production

```bash
npm run build
npm start
```

## Technologies

- Next.js 14 (App Router)
- TypeScript
- React Webcam
- Axios
- CSS Modules

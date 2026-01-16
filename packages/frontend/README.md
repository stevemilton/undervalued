# Undervalued Frontend

Next.js frontend for the UK Property Opportunity Finder.

## Setup

```bash
npm install
npm run dev
```

## Development

- Frontend runs at http://localhost:3000
- API URL configured via `NEXT_PUBLIC_API_URL`

## Structure

```
src/
├── app/              # Next.js App Router pages
├── components/       # React components
│   ├── ui/          # shadcn/ui primitives
│   ├── layout/      # Layout components
│   ├── opportunities/
│   └── properties/
├── hooks/           # React Query hooks
├── lib/             # Utilities (api, formatting)
└── types/           # TypeScript interfaces
```

## Testing

```bash
npm run test          # Run tests
npm run test:ui       # With UI
npm run test:coverage # Coverage report
```

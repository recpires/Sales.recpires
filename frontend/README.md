# Sales Frontend

A modern React application built with Vite, TypeScript, and Tailwind CSS.

## Features

- ⚛️ React 19
- 🔷 TypeScript for type safety
- ⚡ Vite for fast development
- 🎨 Tailwind CSS for styling
- 🧩 Reusable component library with full type definitions

## Components

### Common Components

All components are fully typed with TypeScript interfaces and props validation.

- **Button** - Multiple variants (primary, secondary, outline, danger, success) and sizes (sm, md, lg)
- **Card** - Flexible card component with Header, Title, Content, and Footer subcomponents
- **Input** - Form input with label, error states, and helper text
- **Badge** - Status badges with different variants and sizes

### Layout Components

- **Layout** - Main layout wrapper with header and footer

## Getting Started

### Install dependencies
```bash
npm install
```

### Run development server
```bash
npm run dev
```

### Build for production
```bash
npm run build
```

### Preview production build
```bash
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── common/          # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   └── index.ts
│   └── layout/          # Layout components
│       └── Layout.tsx
├── pages/               # Page components
├── App.tsx              # Main app component
├── main.tsx             # Entry point
└── index.css            # Global styles with Tailwind
```

## TypeScript Configuration

The project uses strict TypeScript configuration with:
- Strict mode enabled
- No unused locals/parameters checking
- Path aliases configured (`@/` points to `src/`)

All components use proper TypeScript types:
- Props are defined using `interface` with proper inheritance
- HTML attributes are extended using `HTMLAttributes` and similar types
- Type-safe variants and sizes using union types

## Tailwind Configuration

Tailwind CSS is configured in `tailwind.config.js` with content paths set to scan all JS/JSX/TS/TSX files in the `src` directory.

The global stylesheet (`src/index.css`) includes Tailwind directives:
- `@tailwind base`
- `@tailwind components`
- `@tailwind utilities`
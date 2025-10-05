#!/usr/bin/env bash
# Build script for frontend deployment on Render

set -o errexit

# Install dependencies
npm ci

# Build the application
npm run build

# Copy _redirects to dist for SPA routing (if exists)
if [ -f "_redirects" ]; then
  cp _redirects dist/_redirects
fi

# Copy _headers to dist for security headers (if exists in public)
if [ -f "public/_headers" ]; then
  cp public/_headers dist/_headers
fi

echo "Frontend build completed successfully!"

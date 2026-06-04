# =============================================================================
# Dockerfile — ReactJS Frontend
# =============================================================================

FROM node:18-alpine AS base
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

COPY . .

# ── Development stage ─────────────────────────────────────────────
FROM base AS development
EXPOSE 3000
CMD ["npm", "start"]

# ── Production build stage ────────────────────────────────────────
FROM base AS builder
RUN npm run build

# ── Production serve (nginx static) ──────────────────────────────
FROM nginx:alpine AS production
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx-spa.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

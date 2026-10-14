# ── Stage 1: Build Vite React SPA ───────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Build arguments for Vite environment
ARG VITE_SKILL_API_URL=http://localhost:5001/api
ARG VITE_OPPORTUNITY_API_URL=http://localhost:5002/api

ENV VITE_SKILL_API_URL=$VITE_SKILL_API_URL
ENV VITE_OPPORTUNITY_API_URL=$VITE_OPPORTUNITY_API_URL

RUN npm run build

# ── Stage 2: Serve with Nginx ────────────────────────────────────────────────
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# ---------- Stage 1: build the React app with Node ----------
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html vite.config.js ./
COPY public ./public
COPY src ./src
RUN npm run build

# ---------- Stage 2: serve the static files with Nginx (non-root) ----------
FROM nginxinc/nginx-unprivileged:1.29-alpine
# Apply Alpine security updates. The base image can lag behind fixed packages,
# which Trivy reports as HIGH vulnerabilities. Switch back to the nginx user afterwards.
USER root
RUN apk upgrade --no-cache
USER 101
# Address of the FastAPI backend. Overridden in Kubernetes.
ENV BACKEND_URL=http://backend:8000
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
# The nginx-unprivileged image already runs as user 101, not root
EXPOSE 8080

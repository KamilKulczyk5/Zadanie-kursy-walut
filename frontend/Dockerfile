# === build Angular ===
FROM node:20-alpine AS build
WORKDIR /app

COPY frontend-app/package*.json ./frontend-app/
RUN cd frontend-app && npm ci

COPY frontend-app ./frontend-app
RUN cd frontend-app && npm run build

# === serve with nginx ===
FROM nginx:alpine
COPY --from=build /app/frontend-app/dist/frontend-app/browser/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

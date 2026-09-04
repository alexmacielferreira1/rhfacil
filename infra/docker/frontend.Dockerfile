# syntax=docker/dockerfile:1
FROM node:24.19.0-alpine3.23

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN --mount=type=cache,id=npm-global-cache,target=/root/.npm npm ci
COPY frontend/ ./
RUN chown -R node:node /app
USER node

EXPOSE 5173
CMD ["npm", "run", "dev"]

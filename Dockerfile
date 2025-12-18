# Build frontend
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build the application
RUN npm run build

# Production nginx image
FROM nginx:alpine

# Copy built frontend files
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# Simple nginx image with pre-built frontend
FROM nginx:alpine

# Copy pre-built frontend files
COPY frontend/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

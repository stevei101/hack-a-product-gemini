# Stage 1: Build with Bun
FROM oven/bun:latest AS build

WORKDIR /app

# Copy package files for optimized caching. This layer only changes
# if your dependencies change, making subsequent builds much faster.
COPY package.json bun.lockb* ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy the rest of the source code
COPY . .

# Build the application
RUN bun run build

# Stage 2: Serve static files with NGINX
FROM nginx:1.27-alpine-slim

# Copy built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy our custom nginx configuration, which is better for SPAs
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check to ensure the server is responsive. Kubernetes will use this
# to automatically restart the container if it becomes unhealthy.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
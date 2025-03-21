FROM node:22.14.0-alpine AS build
WORKDIR /app

# Copy package files first for better caching
COPY front-end/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source code
COPY front-end/ .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
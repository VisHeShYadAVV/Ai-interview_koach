# Stage 1: Build the Angular app
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve the app with nginx
FROM nginx:alpine

# Copy built files from stage 1
COPY --from=build /app/dist/smartkoach-frontend /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 4200

CMD ["nginx", "-g", "daemon off;"]

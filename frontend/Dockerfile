FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the frontend (use localhost since frontend is served to host browser)
RUN npm run build

# Serve using a simple HTTP server
RUN npm install -g serve

EXPOSE 3000

# Serve the built app on port 3000
CMD ["serve", "-s", "dist", "-l", "3000"]

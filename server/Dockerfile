# Use a lightweight Node.js Alpine image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json first to leverage Docker cache
COPY package*.json ./

# Install production dependencies
RUN npm install --only=production

# Copy the rest of the application code
COPY . .

# Expose the WebSocket port (default is 8080)
EXPOSE 8080

# Command to run the application
CMD ["npm", "start"]

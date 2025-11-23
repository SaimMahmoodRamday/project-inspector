# # Stage 1 - Build the frontend
# FROM node:18 AS build
# WORKDIR /app
# COPY package.json package-lock.json ./
# RUN npm install
# COPY . .
# RUN npm run build

# # Stage 2 - Serve the frontend with nginx
# FROM nginx:alpine
# COPY --from=build /app/dist /usr/share/nginx/html
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]

# New 02

# # Stage 1 - Build the frontend
# FROM node:18 AS build
# WORKDIR /app
# COPY package.json package-lock.json ./
# RUN npm install
# COPY . .
# RUN npm run build

# # Stage 2 - Serve the frontend with nginx
# FROM nginx:alpine
# COPY --from=build /app/dist /usr/share/nginx/html
# COPY nginx.conf /etc/nginx/conf.d/default.conf
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]

# New 03

# Stage 1 - Build frontend
FROM node:18 AS build
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies (including Tailwind)
RUN npm install

# Copy source code
COPY . .

# Build frontend
RUN npm run build

# Stage 2 - Serve with nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

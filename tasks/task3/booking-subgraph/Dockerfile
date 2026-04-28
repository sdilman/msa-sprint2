FROM node:18

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

# booking.proto is mounted via docker-compose volume at runtime
CMD ["node", "index.js"]

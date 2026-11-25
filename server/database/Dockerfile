FROM node:22-bookworm-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY . .
ENV PORT=3030
EXPOSE 3030
USER node
CMD ["node", "app.js"]

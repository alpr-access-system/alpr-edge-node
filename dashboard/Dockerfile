FROM node:lts-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

# Vite por defecto escucha en localhost, --host lo expone para que funcione en Docker
CMD ["npm", "run", "dev", "--", "--host"]

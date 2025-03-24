# Etapa de desarrollo
FROM node:18-slim

# Instalar pnpm
RUN npm install -g pnpm

# Establecer directorio de trabajo
WORKDIR /app

# Copiar package.json y pnpm-lock.yaml (si existe)
COPY frontend/package.json ./
COPY frontend/pnpm-lock.yaml* ./

# Instalar dependencias
RUN pnpm install

# Copiar el resto de archivos de la aplicación
COPY frontend/ ./

# Exponer el puerto para desarrollo
EXPOSE 4321

# Comando para iniciar la aplicación en modo desarrollo
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0"]

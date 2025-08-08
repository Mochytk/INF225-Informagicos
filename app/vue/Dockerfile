# Imagen base con Node.js
FROM node:18

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos del proyecto
COPY . .

# Instalar dependencias
RUN npm install

# Compilar el frontend para producción
RUN npm run build

# Usar Nginx para servir los archivos
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html

# Exponer el puerto 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

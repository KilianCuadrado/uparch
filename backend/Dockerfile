# == 1. IMAGEN BASE ==
# Usamos una versión ligera de Python 3.11
FROM python:3.11-slim

# == 2. DIRECTORIO DE TRABAJO ==
# Esta es la carpeta dentro del contenedor donde vivirá nuestra app
WORKDIR /app

# == 3. INSTALAR DEPENDENCIAS ==
# Copiamos el archivo requirements.txt directamente desde la misma carpeta backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# == 4. COPIAR EL CÓDIGO ==
# Copiamos el resto del código del backend (main.py, etc.) dentro de /app
COPY . .

# == 5. EXPONER EL PUERTO ==
EXPOSE 8000

# == 6. INICIAR LA APLICACIÓN ==
# Ya no es "backend.main:app" sino "main:app" porque el código se copió a la raíz de /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11

WORKDIR /app

# Copiar requirements primero
COPY requirements.txt /app/requirements.txt

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar el resto del código
COPY . /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

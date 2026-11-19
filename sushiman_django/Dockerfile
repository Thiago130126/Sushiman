FROM python:3.12-slim

# Variável de ambiente que impede a criação de arquivos .pyc 
# 1 = Não; 0 = Sim
ENV PYTHONDONTWRITEBYTECODE 1

# Variável de ambiente que impede o buffer do Python de armazenar a saída do programa em memória, garantindo que a saída seja exibida imediatamente no console.
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "sushiman_django.wsgi:application", "--bind", "0.0.0.0:8000"]
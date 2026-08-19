# Python 3.11 image bilan boshlaymiz
FROM python:3.11-slim

# Yaratilgan fayllar image ichida kechikmasligi uchun bu amallarni bajaramiz
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Tizimni yangilaymiz va kerakli paketlarni o'rnatamiz
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean

# Loyihamiz fayllarini joylash uchun papka yaratamiz
WORKDIR /app

# requirements.txt faylini nusxalab olamiz
COPY requirements.txt /app/

# Django va boshqa kerakli kutubxonalarni o'rnatamiz
RUN pip install --no-cache-dir -r requirements.txt

# Barcha loyihani nusxalaymiz
COPY . /app/

# Django collectstatic buyruqni bajarmaslik uchun
RUN mkdir -p /vol/web/static && chmod -R 755 /vol/web/static

# Bo'sh portni eshitish uchun
EXPOSE 8000

# Loyihani ishga tushiramiz
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "projectname.wsgi:application"]

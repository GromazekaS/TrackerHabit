# 🚀 Трекер Привычек
Курсовой проект по DjangoRestFramework

# Подготовка

Клонируйте проект и перейдите в папку

git clone <repository-url>

cd pythonproject2

# Создайте файл настроек
cp .env.example .env

Отредактируйте файл .env:

env
SECRET_KEY=ваш-секретный-ключ

TELEGRAM_BOT_TOKEN=токен-бота-из-telegram

POSTGRES_PASSWORD=пароль-для-бд


# Запуск всех сервисов
docker-compose up -d

# Выполнить миграции
docker-compose exec django python manage.py migrate

# Создать суперпользователя
docker-compose exec django python manage.py createsuperuser

# API сервер:

curl http://localhost:8000/api/v1/public-habits/

или откройте в браузере: http://localhost:8000/api/docs/

### База данных:

docker-compose exec postgres pg_isready -U habit_user -d habit_db

### Redis:


docker-compose exec redis redis-cli ping

Должен вернуть: PONG

### Celery:

docker-compose exec celery_worker celery -A config statu

# Просмотр логов
docker-compose logs -f

# Остановка проекта
docker-compose down

# Перезапуск конкретного сервиса
docker-compose restart django
# Тестирование
bash
# Запуск тестов
docker-compose exec django python manage.py test
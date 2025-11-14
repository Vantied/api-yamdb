# Yatube API 

## Описание 

YaMDb (Yet another Movie Database) — это RESTful API для социальной платформы, где пользователи могут оставлять отзывы и оценки на различные произведения: фильмы, книги и музыку.

**Основные функции:**
- Публиковать отзывы на произведения
- Ставить оценки от 1 до 10
- Комментировать отзывы других пользователей
- Организовывать произведения по категориям и жанрам
- Управлять пользователями с разными уровнями доступа

**Важно:** В YaMDb не хранятся сами произведения (фильмы, музыка), только метаданные и пользовательский контент.

## Стек технологий

- **Backend:** Python 3.12.7, Django 5.2.8, Django REST Framework 3.15.2
- **Аутентификация:** JWT (Simple JWT)
- **База данных:** SQLite
- **Документация:** OpenAPI (ReDoc)
- **Фильтрация:** Django Filter

## Установка

### Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/yandex-praktikum/api-yamdb.git
```

```
cd api-yamdb
```

### Cоздать и активировать виртуальное окружение:

Для Windows

```
python -m venv venv
source venv/Scripts/activate
```

Для Linux/MacOS

```
python3 -m venv venv
source venv/bin/activate
```

### Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

### Создать и применить миграции:

Для Windows

```
python manage.py makemigrations
python manage.py migrate
```

Для Linux/MacOS

```
python3 manage.py makemigrations
python3 manage.py migrate
```

## Примеры запросов к API и ответы:

### Регистрация нового пользователя:

**Запрос**

```
curl -X POST http://127.0.0.1:8000/api/v1/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "newuser"}'
```

**Ответ**

```
{
  "email": "user@example.com",
  "username": "newuser"
}
```

### Получение JWT токена:

**Запрос**

```
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "confirmation_code": "123456"}'
```

**Ответ**

```
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Получение своего профиля

**Запрос**

```
curl -X GET http://127.0.0.1:8000/api/v1/users/me/ \
  -H "Authorization: Bearer <ваш_JWT_токен>"
```

**Ответ**

```
{
  "username": "newuser",
  "email": "user@example.com",
  "first_name": "",
  "last_name": "",
  "bio": "",
  "role": "user"
}
```

### Создание отзыва на произведение

**Запрос**

```
curl -X POST http://127.0.0.1:8000/api/v1/titles/1/reviews/ \
  -H "Authorization: Bearer <ваш_JWT_токен>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Отличный фильм!", "score": 9}'
```

**Ответ**

```
{
  "id": 1,
  "text": "Отличный фильм!",
  "author": "newuser",
  "score": 9,
  "pub_date": "2024-01-15T10:30:00Z"
}
```

## Документация

**После запуска сервера полная документация API доступна по адресу:** 

```
ReDoc: http://127.0.0.1:8000/redoc/

Swagger: http://127.0.0.1:8000/swagger/
```

## Разработчики

Иван Богатов - Произведения и импорт данных
Башкатов Кирилл - Аутентификация и пользователи
Максим Пятаев - Отзывы и рейтинги

**Тимлид:** Иван Богатов

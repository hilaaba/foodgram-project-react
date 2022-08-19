# Foodgram

## Описание проекта:

Проект Foodgram позволяет публиковать рецепты, подписываться на 
публикации других пользователей, добавлять понравившиеся рецепты в «Избранное», 
а перед походом в магазин скачивать сводный список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.

Проект запущен по адресу:

Документация по API:

## Технологии:
Python 3.8  
Django 2.2.19  
Django REST Framework 3.13.1  
Djoser 2.1.0  
PostgreSQL 12  
Docker 20.10.17
Gunicorn 20.1.0  
Nginx 1.19.3

## Как запустить проект локально в docker-контейнерах:

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/hilaaba/foodgram-project-react.git
```

```bash
cd foodgram-project-react
```

Перейти в папку развёртывания инфраструктуры:

```bash
cd ../infra
```
Шаблон наполнения env-файла:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

Запустить приложение в docker-контейнерах:

```bash
docker-compose up -d --buld
```

Выполнить миграции и сбор статики:

```bash
docker-compose exec web python3 manage.py migrate
```
    
```bash
docker-compose exec web python3 manage.py collectstatic --no-input
```

Теперь проект доступен по адресу <http://127.0.0.1/>,  
документация по API проекта - по адресу <http://127.0.0.1/api/docs/>.

Заполнить данными таблицу ингредиентов можно командами:

```
docker-compose exec web python3 manage.py load_data_to_db

```

## Создать суперпользователя

```bash
docker-compose exec web python3 manage.py createsuperuser
```

Теперь по адресу <http://127.0.0.1/admin/> доступна админка проекта.

## Остановить работу всех контейнеров и удалить

```bash
docker-compose down -v
```

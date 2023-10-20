# Сайт Foodgram
![example workflow](https://github.com/smsalatik/foodgram-project-react/actions/workflows/main.yml/badge.svg)


## **Описание проекта**
Сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать и скачивать список продуктов, которые нужно купить для приготовления выбранных блюд.

## **Технологии:**

* [Python 3.9](https://www.python.org/downloads/)
* [Django 3.2.3](https://www.djangoproject.com/download/)
* [djangorestframework 3.12.4](https://pypi.org/project/djangorestframework/#files)
* [djoser 2.1.0](https://pypi.org/project/djoser/#files)
* [webcolors 1.11.1](https://pypi.org/project/webcolors/1.11.1/)
* [gunicorn 20.1.0](https://pypi.org/project/gunicorn/20.1.0/)
* [psycopg2-binary 2.9.6](https://pypi.org/project/psycopg2-binary/#files)
* [pytest-django 4.4.0](https://pypi.org/project/pytest-django/)
* [pytest-pythonpath 0.7.3](https://pypi.org/project/pytest-pythonpath/)
* [pytest 6.2.4](https://pypi.org/project/pytest/)
* [PyYAML 6.0](https://pypi.org/project/PyYAML/)
* [python-dotenv 1.0.0](https://pypi.org/project/python-dotenv/)

## Локальный запуск проекта

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/smsalatik/foodgram-project-react.git
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение, установить зависимости:

```bash
python3 -m venv venv && \ 
    source venv/scripts/activate && \
    python -m pip install --upgrade pip && \
    pip install -r backend/requirements.txt
```

Установите [docker compose](https://www.docker.com/) на свой компьютер.

Запустите проект через docker-compose:

```bash
docker compose -f docker-compose.yml up --build -d
```

Выполнить миграции:

```bash
docker compose -f docker-compose.yml exec backend python manage.py migrate
```

Соберите статику и скопируйте ее:

```bash
docker compose -f docker-compose.yml exec backend python manage.py collectstatic  && \
docker compose -f docker-compose.yml exec backend cp -r /app/static_backend/. /backend_static/
```

## .env

В корне проекта создайте файл .env и пропишите в него свои данные.

Пример:

```apache
SECRET_KEY = 'my_secret_key'
POSTGRES_DB=user
POSTGRES_USER=user
POSTGRES_PASSWORD=password
DB_NAME=user
DB_HOST=db
DB_PORT=5432 
DEBUG=False
ALLOWED_HOSTS = '*******.****.net, **.**.**.**, 127.0.0.1, localhost'
```

## Workflow

Для использования CI/CD: в репозитории GitHub Actions `Settings/Secrets/Actions` прописать Secrets - переменные окружения для доступа к сервисам:

```
DOCKER_USERNAME                # имя пользователя в DockerHub
DOCKER_PASSWORD                # пароль пользователя в DockerHub
HOST                           # ip_address сервера
USER                           # имя пользователя
SSH_KEY                        # приватный ssh-ключ (cat ~/.ssh/id_rsa)
PASSPHRASE                     # кодовая фраза (пароль) для ssh-ключа
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
TELEGRAM_TO                    # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN                 # токен бота (получить токен можно у @BotFather, /token, имя бота)
```

При push в ветку main автоматически отрабатывают сценарии:

* *tests* - проверка кода на соответствие стандарту PEP8 и запуск pytest. Дальнейшие шаги выполняются только если push был в ветку main;
* *build\_and\_push\_to\_docker\_hub* - сборка и доставка докер-образов на DockerHub* *deploy* - автоматический деплой проекта на боевой сервер. Выполняется копирование файлов из DockerHub на сервер;
* *send\_message* - отправка уведомления в Telegram.

## Автор
Магомедов Ахмад - [GitHub](https://github.com/smsalatik/)
# praktikum_new_diplom

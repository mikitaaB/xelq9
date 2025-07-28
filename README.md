# Django JSON Uploader

Веб-приложение для загрузки и просмотра JSON файлов с данными, развернутое с использованием Django + Gunicorn + Nginx.

## Развертывание на сервере

### 1. Обновление пакетов apt

Перед установкой сервисов обновить пакеты на сервере:

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Установка Python

Установить Python и сопутствующие пакеты:

```bash
sudo apt install python3 python3-pip python3-venv -y
```

Проверить установку:

```bash
python3 --version
```

### 3. Создание аккаунта PostgreSQL и базы данных

Установить PostgreSQL:

```bash
sudo apt install postgresql postgresql-contrib -y
```

Создать базу данных и пользователя:

```bash
sudo -u postgres psql
```

В PostgreSQL выполнить:

```sql
CREATE DATABASE jsondb;
CREATE USER jsonuser WITH PASSWORD 'your_secure_password';
ALTER ROLE jsonuser SET client_encoding TO 'utf8';
ALTER ROLE jsonuser SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE jsondb TO jsonuser;
\q
```

### 4. Настройка виртуальной среды Python для Django

Создать директорию проекта и виртуальное окружение:

```bash
mkdir ~/jsonuploader && cd ~/jsonuploader
git clone https://github.com/mikitaaB/xelq9.git .
python3 -m venv venv
source venv/bin/activate
```

### 5. Установка Django, Gunicorn и psycopg2

Установить необходимые пакеты:

```bash
pip install -r requirements.txt
```

### 6. Настройка проекта

Создать и заполнить данными .env файл

В поле ALLOWED_HOSTS указать адреса, которым разрешено подключение:

```python
ALLOWED_HOSTS = [
    'your_server_ip',
    'your_domain.com',
    'localhost'
]
```

Применить изменения в базе данных и создать суперпользователя:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

### 7. Создание файлов сокета и systemd

Создать сокет Gunicorn в `/etc/systemd/system/gunicorn.socket`:

```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

```
[Unit]
Description=Gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Создать systemd-юнит в `/etc/systemd/system/gunicorn.service`:

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```
[Unit]
Description=Gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=user
Group=www-data
WorkingDirectory=/home/user/jsonuploader
ExecStart=/home/user/jsonuploader/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          jsonuploader.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 8. Активация сокета и проверка systemd

Активировать и запустить сервисы:

```bash
sudo systemctl enable gunicorn.socket
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.service
sudo systemctl start gunicorn.service
```

Проверить статус:

```bash
sudo systemctl status gunicorn
```

### 9. Настройка Nginx

Установить Nginx:

```bash
sudo apt install nginx -y
```

Создать конфигурационный файл:

```bash
sudo nano /etc/nginx/sites-available/jsonuploader
```

```
server {
    listen 80;
    server_name your_server_ip your_domain.com;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    location /static/ {
        root /home/osboxes/jsonuploader;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }

    client_max_body_size 10M;
}
```

Создать символическую ссылку:

```bash
sudo ln -s /etc/nginx/sites-available/jsonuploader /etc/nginx/sites-enabled
```

Проверить конфигурацию:

```bash
sudo nginx -t
```

Запустить Nginx:

```bash
sudo systemctl restart nginx
```

### 10. Запуск проекта

Перезапустить Gunicorn-сервис:

```bash
sudo systemctl restart gunicorn
```

Открыть браузер и перейти по адресу сервера.

Админ-панель доступна по адресу: `http://your_server_ip/admin/`

### 11. Получение SSL/TLS-сертификата

Установить Certbot:

```bash
sudo apt install certbot python3-certbot-nginx -y
```

Получить сертификат:

```bash
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

Проверить автоматическое обновление:

```bash
sudo certbot renew --dry-run
```

### Формат JSON файла

```json
[
    {
        "name": "Иван Иванов",
        "email": "ivan@example.com",
        "age": 30,
        "position": "Разработчик",
        "hire_date": "2023-01-15_10:30"
    },
    {
        "name": "Мария Петрова",
        "email": "maria@example.com",
        "age": 28,
        "position": "Дизайнер",
        "hire_date": "2023-02-20_09:00"
    }
]
```
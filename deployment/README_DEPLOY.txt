# Инструкция по деплою PayForge на VPS (Ubuntu 22.04+)

1.  **Подготовка сервера:**
    - Обновите систему: `sudo apt update && sudo apt upgrade -y`
    - Установите Nginx и Python: `sudo apt install nginx python3-pip python3-venv -y`

2.  **Загрузка файлов:**
    - Создайте папку: `sudo mkdir -p /var/www/payforge`
    - Смените владельца: `sudo chown -R $USER:$USER /var/www/payforge`
    - Закиньте все файлы проекта (index.html, app.py, requirements.txt, и т.д.) в `/var/www/payforge`.

3.  **Настройка окружения:**
    - Зайдите в папку: `cd /var/www/payforge`
    - Создайте venv: `python3 -m venv venv`
    - Активируйте: `source venv/bin/bin`
    - Установите зависимости: `pip install -r requirements.txt`

4.  **Настройка Systemd (Бэкенд):**
    - Скопируйте файл сервиса: `sudo cp deployment/payforge.service /etc/systemd/system/`
    - Запустите: 
      `sudo systemctl start payforge`
      `sudo systemctl enable payforge`

5.  **Настройка Nginx (Фронтенд + Прокси):**
    - Скопируйте конфиг: `sudo cp deployment/nginx.conf /etc/nginx/sites-available/payforge`
    - Включите: `sudo ln -s /etc/nginx/sites-available/payforge /etc/nginx/sites-enabled/`
    - Проверьте: `sudo nginx -t`
    - Перезапустите: `sudo systemctl restart nginx`

6.  **SSL (HTTPS):**
    - Установите Certbot: `sudo apt install certbot python3-certbot-nginx -y`
    - Получите сертификат: `sudo certbot --nginx -d ваш_домен.com`

**Готово! Теперь ваш сайт будет доступен по HTTPS с работающей регистрацией и ботом.**

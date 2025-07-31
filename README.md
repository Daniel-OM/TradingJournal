# Trading Journal Web App

This is a web application built with **Flask** that functions as a comprehensive trading journal. It is designed to help traders record, analyze, and improve their performance by providing a structured way to track trades, daily watchlists, and trading mistakes.

## 🚀 Purpose

The main goal of this app is to **maximize a trader’s potential** by offering a practical and user-friendly tool to reflect on trading decisions, identify recurring patterns, and reinforce discipline through consistent journaling.

## 🧠 Features

- 📈 **Trade Logging**: Record all trades with essential details like entry/exit, size, strategy, notes, and outcome.
- 🔍 **Watchlists**: Keep a daily record of market watchlists and setups before the trading day.
- ⚠️ **Mistake Tracker**: Log behavioral or execution errors to identify weaknesses and improve decision-making.
- 📊 **Review & Analytics** (optional/future): Visualize statistics and performance trends over time.
- 🔐 **User Authentication** (if implemented): Protect journal entries with login functionality.

## 🛠️ Technologies Used

- **Flask** – Python micro-framework for backend development.
- **Jinja2** – Template engine for dynamic HTML rendering.
- **SQLite / PostgreSQL** – Database for storing user data and journal entries.
- **Bootstrap** – For responsive front-end design (optional).

## 🙌 Contribution

Contributions are welcome! Feel free to submit issues, pull requests, or feature ideas to improve the app.

# Setup

## Git clone
```shell
git clone https://github.com/Daniel-OM/TradingJournal.git
git checkout development
```

## To create the virtual environment
```shell
python -m venv venv
```

## To activate virtual environment
```shell
Windows:
source venv/Script/activate
Linux:
source venv/bin/activate
```

## To install requirements
```shell
pip install -r requirements.txt
```

## Run application
```shell
FLASK_APP=journal.app:app flask run --reload
```

# Application execution in production

## Systemd file for Gunicorn
In the file `sudo nano /etc/systemd/system/trading-journal.service` the next configuration should be added.
```shell
[Unit]
Description=Gunicorn instance to serve TradingJournal app
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/repository
Environment="PATH=/path/to/repository/venv/bin"
ExecStart=/path/to/repository/venv/bin/gunicorn --workers 3 --bind unix:/path/to/repository/trading-journal.sock wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then execute this to start the service.
```shell
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable trading-journal
sudo systemctl start trading-journal
```

## NGINX settings

The following file configuration should be added to the nginx server.
```shell
server {
    listen 80;
    server_name host.com;

    location /trading-journal/ {
        include proxy_params;

        # Elimina /miapp del path antes de pasar al backend
        proxy_pass http://unix:/var/www/TradingJournal/trading-journal.sock;
        proxy_redirect off;

        # Corrige cabeceras para que Flask sepa su base
        proxy_set_header X-Script-Name /trading-journal;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Activate the server.
```shell
# If the symbolic link does not exist
sudo ln -s /etc/nginx/sites-available/host /etc/nginx/sites-enabled/
sudo nginx -t
# Restart
sudo systemctl restart nginx
```

## Give permissions

Make sure to give the needed permissions to the correct user.
```shell
sudo chown -R www-data:www-data /var/www/TradingJournal
```

## Verify the correct release

Visit the page.

Watch the gunicorn logs `systemctl status flask-app`.

Watch the nginx logs `sudo tail -f /var/log/nginx/error.log`.

## Configure HTTPS

Optionally you can add encryption for better security
```shell
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d host.com
```

# Release a new version
```shell
git checkout main
git pull origin main
git merge develop --no-ff
git tag -a vYYYY.MM.DD -m "Release vYYYY.MM.DD"
git push origin vYYYY.MM.DD
```

# Overwrite a release
```shell
git checkout main
git pull origin main
git merge develop --no-ff
git tag -fa vYYYY.MM.DD -m "Release vYYYY.MM.DD"
git push origin vYYYY.MM.DD --force
```

# Auto Update configuration
```shell
chmod u+x /path/to/repository/update.sh
crontab -e
# In the crontab configuration add this:
0 4 * * * /path/to/repository/update.sh >> /var/log/app_name.log 2>&1 # Execute every day at 4 a.m.
```
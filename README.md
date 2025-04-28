# Приложение для ведения статистики по чистке приборов

- хранение данных в базе sqlite

- передача данных с помощью aiogram в телеграмм боте

- Добавить для работы с запросами к базе данных LiteralString

- Отрефачить

## Разбор проекта

.
├── ./clean_bot_run.service # файл сервиса для запуска бота на сервере
├── ./main.py # корневой файл запуска бота
├── ./pyproject.toml
├── ./pyrightconfig.json
├── ./README.md
├── ./src
│   ├── ./src/bot
│   │   ├── ./src/bot/handlers
│   │   │   ├── ./src/bot/handlers/add_company_handler.py
│   │   │   ├── ./src/bot/handlers/add_device_handler.py
│   │   │   ├── ./src/bot/handlers/add_stock_device_handler.py
│   │   │   ├── ./src/bot/handlers/add_type_device_handler.py
│   │   │   ├── ./src/bot/handlers/get_stock_device_handler.py
│   │   │   ├── ./src/bot/handlers/__init__.py
│   │   │   └── ./src/bot/handlers/start_handler.py
│   │   ├── ./src/bot/__init__.py
│   │   └── ./src/bot/keyboard
│   │   ├── ./src/bot/keyboard/__init__.py
│   │   └── ./src/bot/keyboard/keyboard_start.py
│   ├── ./src/db_app.py
│   ├── ./src/__init__.py
│   ├── ./src/interface.py
│   ├── ./src/run_bot.py
│   ├── ./src/secret.py
│   ├── ./src/table.sql
│   ├── ./src/tests
│   │   ├── ./src/tests/conftest.py
│   │   ├── ./src/tests/__init__.py
│   │   ├── ./src/tests/test_bot_api_db.py
│   │   ├── ./src/tests/test_interface.py
│   │   ├── ./src/tests/test_model.py
│   │   ├── ./src/tests/test_query_interface.py
│   │   └── ./src/tests/test_work_sqllite_db.py
│   └── ./src/utils.py
└── ./uv.lock

# Приложение для ведения статистики по чистке приборов

## Для чего

Для ведения базы приборов на складе.

Для удобства добавления прибора и его свойств в базу и
быстрого доступа к ним.

Для помещения прибора в ремонт после очистки.

Для быстрого доступа к статистике по приборам за день.

Для слежением часов работы лампы прибора

Для замены лампы

## Разбор проекта

Структура проекта разделена на четыре модуля

Сам бот, обработчики, клавиатуры.

Интерфейс связи с базой данных.

Схема для генерации строковых запросов к базе.

Модели валидации данных для получения и записи.

## Библиотеки

- Валидация - pydantic
- Тесты - pytest
- env - python-dotenv
- docker - для развертывания на сервере
- sqlite3 - для работы с базой данных

## Запуск и деплой

```bash
# в первый раз
git clone git@github.com:AlexeyKlykin/clean_device.git

# В повторные 
git pull

# сборка
make build # для сборки образа докера
make run # для запуска контейнера bot_cont

# очистка
docker stop bot_cont # для остановки контейнера
docker rm bot_cont # для удаления контейнера
# glow для форматирования md
```

├── ./data_cache # файлы для вставки в бд и тестов
├── ./fill_in_the_table.py # вставка данных в бд при старте
├── ./main.py # файл запуска проекта
└── ./src # ресурсы
├── ./src/bot # ресурсы бота
│   ├── ./src/bot/handlers # обработчики
│   │   ├── ./src/bot/handlers/add_company_handler.py
│   │   ├── ./src/bot/handlers/add_device_handler.py
│   │   ├── ./src/bot/handlers/add_stock_device_handler.py
│   │   ├── ./src/bot/handlers/add_type_device_handler.py
│   │   ├── ./src/bot/handlers/get_stock_device_handler.py
│   │   ├── ./src/bot/handlers/lamp_handler.py
│   │   ├── ./src/bot/handlers/other_components_handler.py
│   │   └── ./src/bot/handlers/start_handler.py
│   ├── ./src/bot/keyboard # клавиатуры
│   │   └── ./src/bot/keyboard/keyboard_start.py
│   └── ./src/bot/states.py # классы для работы fsm
├── ./src/bot_api.py # api работы бота с базой данных
├── ./src/database_interface.py # интерфейс работы с базой
├── ./src/query_scheme.py # набор схем для запросов
├── ./src/scheme_for_validation.py # классы для валидации
├── ./src/secret.py # env
├── ./src/tests # набор тестов
│   ├── ./src/tests/conftest.py
│   ├── ./src/tests/test_bot_api.py
│   ├── ./src/tests/test_database_interface.py
│   ├── ./src/tests/test_query_schemas.py
│   └── ./src/tests/test_scheme.py
└── ./src/utils.py # вспомогательные утилиты

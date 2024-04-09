 ## Сервис покупки товаров для авторизованных пользователей
 # BACKEND часть приложения с авторизацией/аутентификацией и CRUD для товаров и корзины

Использованы следующие технологии : PostgreSQL, FastAPI, Tortoise-ORM, pytest, JWT-bearer token

Запуск проекта - 

    Клонировать репозиторий;
    Активировать виртуальное окружение;
    Установить зависимости;
    Совершить миграции (aerich init-db);
    Команда для запуска (uvicorn src/main:app --reload);
    Адрес интерфейса http://127.0.0.1:8000/docs;
    Команда для запуска тестов (pytest /tests -v).


Методы, доступные неавторизованным пользователям: регистрация, авторизация

Методы, доступные авторизованным пользователям: просмотр товаров, добавление/удаления товара в корзину, 
просмотр корзины, просмотр и изменение данных о пользователе, удаление его, верификация почты

Методы, доступные администраторам/модераторам: CRUD товара, CRUD пользователя, выключение (is_active) товаров и
пользователей, назначение модераторов (только для администратора)

***
# BACKEND API (authorization/authentication and CRUD for products and the basket)

STACK: PostgreSQL, FastAPI, Tortoise-ORM, pytest, JWT-bearer token

DO STEPS FOR START:
    Clone repo;
    Activate virtual environment;
    Install dependencies;
    Perform migrations (aerich init-db);
    Launch command (uvicorn src/main:app --reload);
    SWAGGER documentation address http://127.0.0.1:8000/docs;
    Command to run tests (pytest /tests -v).

Unauthorized user's methods: a registration, an authorization.

Authorized user's methods: a viewing of the products, an adding/removing of the products to/from the basket,
a viewing of the basket, a viewing/changing/deleting the user data, a verifying of the mail

Administrator/moderator's methods: a CRUD of the product, a CRUD of the user, a disabling (is_active) of the 
products/users, an appointment of the moderators (administrator only)
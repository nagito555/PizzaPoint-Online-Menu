# PizzaPoint 🍕

Учебный сайт меню пиццерии на Python Flask, HTML, CSS и базе данных.

## Возможности
- Меню с четырьмя демонстрационными пиццами
- Поиск и фильтрация по категориям
- Регистрация: ФИО, email, телефон, пароль и повтор пароля
- Подтверждение почты шестизначным кодом (код действует 10 минут)
- Вход по email и паролю, личный профиль
- Корзина с изменением количества и подсчётом суммы
- Администратор может добавлять, редактировать и удалять позиции меню
- Пароли хранятся в виде хешей
- SQLite используется как реляционная база данных: таблицы `categories` и `products` связаны внешним ключом `products.category_id`

## Запуск (Windows)
1. Установи Python 3.10+ и распакуй проект.
2. Открой терминал в папке проекта.
3. `pip install -r requirements.txt`
4. `python app.py`
5. Открой http://127.0.0.1:5000

## Демо-администратор
- Email: `admin@pizzapoint.local`
- Пароль: `PizzaAdmin2026!`

Демо-учётные данные не использовать на реальном сайте.

## Код подтверждения email
Без SMTP код подтверждения печатается в консоль Flask. Для отправки настоящих писем задайте переменные окружения SMTP_HOST, SMTP_PORT (587), SMTP_USER, SMTP_PASSWORD и SMTP_FROM. Не коммитьте секреты в репозиторий.

## Структура базы данных и связи
Меню хранится в SQLite. Таблица `categories` содержит категории пицц, а `products.category_id` — внешний ключ на `categories.id`. В `database.py` есть поясняющие комментарии к SQL-запросам с `INNER JOIN`, которые соединяют эти таблицы для получения названия категории. SQLite включает проверку внешних ключей через `PRAGMA foreign_keys = ON`.

Если преподаватель требует именно Microsoft Access, связи `Categories.id` → `Products.category_id` нужно создать в окне **Схема данных / Relationships** Access и включить обеспечение целостности данных. В этой версии Access-режим не реализован.

## Структура
- `app.py` — Flask-маршруты и бизнес-логика
- `database.py` — SQLite база меню с таблицами и связью категорий и пицц
- `authdb.py` — пользователи и корзина
- `templates/` — HTML-шаблоны
- `static/style.css` — оформление

## GitHub: публикация
Создай пустой репозиторий `PizzaPoint-Online-Menu` на GitHub, затем в папке проекта выполни:
```bash
git init
git add .
git commit -m "Initial PizzaPoint project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/PizzaPoint-Online-Menu.git
git push -u origin main
```

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
- SQLite используется по умолчанию; каталог поддерживает дополнительный режим Microsoft Access

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

## Access (дополнительный режим)
Установи Access ODBC driver, создай пустую `PizzaPoint.accdb`, затем в PowerShell: `$env:USE_ACCESS="1"` и `python app.py`. Таблица меню создаётся при запуске. Аккаунты и корзина остаются в SQLite.

## Структура
- `app.py` — Flask-маршруты и бизнес-логика
- `database.py` — база меню / Access
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
"# PizzaPoint-Online-Menu" 

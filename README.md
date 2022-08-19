# Программное средство ks-test

Ks-test создано в рамках решения [тестового задания Python]


Ks-test следит за обновлением документа Google Sheets.

- Работаете с документом в Google Sheets;
- Изменения автоматически вносятся в базу данных.


# Запуск

Ks-test работает в двух контейнерах.
Чтобы запустить его, выполните следующие команды:

```sh
cd ks-test
docker-compose up -d
```

# Результаты работы
Результатом работы ks-test являются:
1. Записи в базе данных, отражающие актуальное состояние документа Google Sheets;
2. Сообщения о заказах, дата доставки которых прошла, в боте Telegram.


# Как работать

Открыть [документ], начать вносить изменения, изменения будут появляться в базе данных.

Записи хранятся в базе данных PostgreSQL, подключение к которой осуществляется по следующим параметрам:
- БД ```orders_db```
- порт ```5432```
- хост ```localhost```
- пользователь ```postgres```
- пароль ```postgres```

Записи хранятся в таблице ```orders```

# Оповещение в Telegram
Ks-test умеет отправлять сообщения в бот Telegram.
Если у какого-то заказа прошёл срок доставки, ks-test будет с определённой периодичностью сообщать об этом.

Для получения оповещений напишите [боту] любое сообщение и ждите оповещений.


# Настройки

Ks-test состоит из логических частей, решающих следующие задачи:

- Взаимодействие с Google API
- Взаимодействие с базой данных
- Взаимодействие с API ЦБ РФ
- Взаимодействие с API Telegram
- Общее управление работой ks-test

Настройка параметров работы данных логических частей осуществляется с использованием переменных окружения, расположенных
в файле ```.env```.

Список переменных, описанных в ```.env```, представлен ниже.
**Взаимодействие с Google API:**
- ```GOOGLE_API_CLIENT_SECRET_FILE```  JSON-файл авторизации Google OAuth2 client id, файл
- ```GOOGLE_API_CLIENT_TOKEN_FILE``` Токен доступа к Google API, файл


**Взаимодействие с Google Sheets:**
- ```SPREADSHEET_ID``` Идентификатор документа Google Sheets, строка
- ```SPREADSHEET_RANGE``` Перечень строк и столбцов документа Google Sheets, используемый ks-test, например 'A:D', строка

**Взаимодействие с БД:**
- ```DB_NAME``` Название БД, строка
- ```DB_USER``` Имя пользователя БД, строка
- ```DB_PASSWORD``` Пароль пользователя БД, строка
- ```DB_HOST``` Хост БД, строка
- ```DB_TABLE``` Название таблицы с заказами в БД, строка
- ```DB_PORT``` Порт БД, строка


**Взаимодействие с API ЦБ РФ:**
- ```CBR_CURRENCY_API_URL``` Ссылка на API ЦБ, отдающее курс валют, строка
- ```CBR_CURRENCY_XML_FIND_PATTERN``` Шаблон поиска необходимой для расчёта валюты, строка

**Взаимодействие с API Telegram**
- ```TG_BOT_TOKEN``` Токен бота, строка
- ```TG_REMINDER_FREQUENCY_SECONDS``` Время в секундах, после которого в бот Telegram "забудет", о каких заказах он уже сообщал, и повторно отправит информацию обо всех просроченных датах доставки. строка или число

**Общее управление работой**
- ```MAIN_SPREADSHEET_REQUEST_FREQUENCY_SECONDS``` Частота опроса документа Google Sheets в секундах



   [тестового задания Python]: <https://unwinddigital.notion.site/unwinddigital/Python-1fdcee22ef5345cf82b058c333818c08>
   [документ]: <https://docs.google.com/spreadsheets/d/17QEW5pedoH2n5pP1Jsny7MZnJAWQnOMrWhSjTGZ2vO8/edit#gid=0>
   [боту]: <t.me/YacynaPavel_ks_test_bot>

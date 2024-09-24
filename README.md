Проект для обработки событий GitHub через вебхуки и отправки уведомлений в Telegram с использованием кастомных шаблонов Jinja2. Проект является форком [репозитория](https://github.com/leitosama/github-telegram-webhook).

## Структура проекта

```bash
github-telegram-webhook
├── .env                          
├── .gitignore                    
├── main_local.py                 
├── main_yandex.py                
├── README.md                     
├── requirements.txt              
├── templates                     
│   └── default_set               
│       ├── issue_comment.j2      
│       ├── issues.j2             
│       ├── pull_request.j2       
│       ├── push.j2               
│       └── release.j2            
├── tests                         
│   ├── expected_messages         
│   │   ├── issue_comment_expected_1.txt  
│   │   └── issues_expected_1.txt 
│   ├── payloads                  
│   │   ├── issue_comment         
│   │   │   └── issue_comment_test_1.json  
│   │   ├── issues                
│   │   │   ├── issues_test_1.json  
│   │   │   └── issues_test_2.json  
│   │   ├── pull_request          
│   │   │   └── pull_request_test_1.json  
│   │   ├── push                  
│   │   │   └── push_test_1.json  
│   │   └── release               
│   │       ├── release_test_1.json  
│   │       └── release_test_2.json  
│   ├── __init__.py               
│   ├── test_create_message.py    
│   ├── test_extract_and_clean_urls.py  
│   └── test_rendering.py
```

## Установка
1. Склонируйте репозиторий:
    ```
    git clone https://github.com/Reversenant/github-telegram-webhook.git
    cd github-telegram-webhook
    ```
2. Создайте виртуальное окружение и активируйте его:
    ```
    python -m venv venv
    source venv/bin/activate  # На Windows используйте `venv\Scripts\activate.ps1`
    ```
3. Установите зависимости:
    ```
    pip install -r requirements.txt
    ```
4. Настройте переменные окружения. В файл .env в корневом каталоге добавьте следующие строки:
    ```
    BOT_TOKEN=<токен Вашего Telegram бота>
    GITHUB_SECRET_Test-repo=<секрет GitHub для репозитория>
    ```
    Вместо "Test-repo" в GITHUB_SECRET_Test-repo добавьте название Вашего репозитория. (GITHUB_SECRET_<имя_репозитория>)

## Использование
### Локальный запуск через Localtunnel

Локальная работа происходит внутри файла _main_local.py_.  
В переменных окружения (.env) укажите токен для Вашего бота и любое слово в качестве GitHub секрета.  
```
BOT_TOKEN=<your bot token>
GITHUB_SECRET_<имя_репозитория>=<random word>
```
Измените REPO_TOPIC_MAP так, чтобы он соответствовал следующей структуре:  
```python
REPO_TOPIC_MAP = {
    "<имя_репозитория>": {
        "topics": ["chat_id:topic_id"],
        "template_set": "your_set"
    }
}
```
Если Вам необходимо, чтобы сообщения приходили в конкретный топик в вашей группе:
```python
"topics": ["chat_id:topic_id"]
```
Если Вам необходимо, чтобы сообщения приходили в разные группы/топики (добавлять можно неограниченное количество):
```python
"topics": ["chat_id_1:topic_id_1", "chat_id_2:topic_id_2","chat_id_3"]
```
Вы также можете добавить несколько репозиториев, которые будут отправлять уведомления в заданные чаты, добавив к каждому из них соответствующий шаблон:
```python
{
    "<имя_репозитория_1>": {
        "topics": ["chat_id_1:topic_id_1"],
        "template_set": "set_1"
    },
    "<имя_репозитория_2>": {
        "topics": ["chat_id_2"],
        "template_set": "set_2"
    }
}
```
Далее, установите LocalTunnel - [Ссылка на GitHub](https://github.com/localtunnel/localtunnel)

Запустите локальный сервер и откройте его через Localtunnel:
```bash
lt --port 5000
```
Это создаст публичный URL (например, https://your-subdomain.loca.lt). Скопируйте этот URL для использования в GitHub репозитории.

Перейдите в ваш репозиторий на GitHub:
```
1. Зайдите в Settings > Webhooks.
2. Нажмите Add webhook.
3. В поле Payload URL вставьте URL Localtunnel (например, https://your-subdomain.loca.lt/webhook), не забудьте указать /webhook или другой путь, на который ваш сервер ожидает события от GitHub.
4. Установите Content type на application/json.
5. Выберите события, которые должны срабатывать (например, push, pull request, issue comments).
6. Нажмите Add webhook.
```
Теперь каждый раз, когда вы пушите изменения, создаете issue или pull request, GitHub будет отправлять POST запрос на ваш локальный сервер через Localtunnel URL.

## Запуск в Яндекс Облаке
Для развертывания в Яндекс Облаке используется файл main_yandex.py. Чтобы настроить и запустить приложение в Яндекс Функции:
```
1. Создайте функцию в Яндекс Облаке с поддержкой Python.
2. Загрузите зависимости, добавив нужные библиотеки через интерфейс или в ZIP-архиве.
3. Настройте переменные окружения.
4. Убедитесь, что обработчиком указан ya_handler из файла main_yandex.py.
```
## Настройка шаблонов
Шаблоны для уведомлений находятся в папке templates. По умолчанию доступен набор `default_set`. Каждый файл шаблона соответствует конкретному событию GitHub и использует данные, переданные вебхуком.

Файлы шаблонов:
```
issue_comment.j2 — шаблон для комментариев к issue.
issues.j2 — шаблон для создания или закрытия issue.
pull_request.j2 — шаблон для pull request.
push.j2 — шаблон для push событий.
release.j2 — шаблон для релизов.
```
Измените эти шаблоны в соответствии с вашими требованиями к форматированию сообщений для Telegram.

## Тестирование
Тесты проекта находятся в папке tests. Они включают следующие сценарии:
- Проверка генерации сообщений на основе шаблонов.
- Проверка обработки URL и медиафайлов.
- Проверка рендеринга сообщений из GitHub payload позволит определить корректность шаблонов и форматов сообщений.
# Парсер мобильного API OZON

Составлен по ТЗ https://www.notion.so/Python-dev-20dfce450de74b4b9b2d4a0d0c93bc29

#### Состоит из 1 worker'а, скачивающего список товаров из категории по Ozon API и парсеров, обрабатывающих эти JSON списки (После получения списков, worker кладет их в топик ozon-category kafka, откуда его и берет parser; после обработки parser складывает товары в топик ozon-products)

#### В проекте уже есть kafka и zookeeper, поэтому он не зависит от внешних модулей

#### Требования:
* Docker
* Python3
* Незанятые имена для контейнеров zookeeper, kafka, ozon-worker, kafka-project_ozon-parser_
* Отсутствие docker сети, перекрывающей адреса 173.18.0.0/16

### Инструкция по установке:
* Склонировать проект в папку
* Запустить файл control.py с флагом start

### Использование:

Сделать cURL запрос на адрес worker'а с ссылкой, которую нужно обработать (пример ниже)
```
curl -H "Content-Type: application/json" -d '{"link": "https://www.ozon.ru/category/kompyutery-i-komplektuyushchie-15690/"}' 173.18.0.9
```

#### Варианты ответов:
* StatusCode = 200 - ссылка успешно обработалась
* StatusCode = 400 - получены некорректные данные 
* StatusCode = 500 - внутренняя ошибка (стоит посмотреть логи)

### Принцип работы:

#### docker-compose.yml:
* Создаются 4 основных контейнера (kafka, zookeeper, ozon-worker, kafka-project_ozon-parser_ и дополнительные парсеры (если указано в настройках))

#### control.py:
Есть возможность запустить с 3-мя флагами:
* `python control.py start` - первоначальная настройка/запуск модуля
* `python control.py stop` - остановка модуля
* `python control.py remove` - остановка модулей и удаление образов worker'a и parser'a, а также docker сети

#### settings.json:
Устанавливается кол-во парсеров, которые неоходимо запустить (в дополнение к ним создаются partition'ы в топике ozon-category)

#### logs:
Создается папка с логами, куда записываются логи worker'a и каждого из парсеров отдельно

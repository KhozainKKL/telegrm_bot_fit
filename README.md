<div class="header">
    <h1> Телеграмм бот для фитнес-клуба Loft Gym</h1>
    <img alt="лого" src="main/media/Новая папка/logo.jpg" width="200" height="200"/>
</div>
<div class="query">
    <h2>Задачи:</h2>
    <h3>Клиентская часть (бот)</h3>
    <ul>
        <li>Запись на групповые занятия.</li>
        <li>Отслеживание записей</li>
        <li>Получение оперативной информации обо всех изменениях</li>
        <li>Получение рассылок</li>
    </ul>
    <h3>Административная часть:</h3>
    <ul>
        <li>Отслеживание клиентов</li>
        <li>Мониторинг количества записей по гистограмме</li>
        <li>Опубликование рассылок</li>
        <li>Внесение изменений (отмена) в занятия</li>
        <li>Импорт (экспорт) проведенных записей</li>
    </ul>
</div>
<div class="func">
    <h2>Настройка:</h2>

`.env`
```dotenv
SECRET_KEY=КЛЮЧ DJANGO
DEBUG=False
TG_API_KEY=Ключ Телеграмм бота
LOGLEVEL=info
```

<p><b>Запуск проекта через Docker</b></p>

```shell
  docker-compose up --build
```
<p><b>Запуск локального проекта на 8000 порту в директории main</b></p>

```shell
pip install -r ../requirements.txt 
```

```shell
python manage.py collectstatic
```

```shell
python manage.py migrate && python manage.py runserver
```
<p>Запуск бота</p>

```shell
python manage.py run_bot
```

<p>Запуск локального celery</p>

```shell
celery -A main worker -l info
```
<p>Запуск локального flower</p>

```shell
celery -A main flower --port=5555
```
<i>Примечание: grafana и loki  локально не запускаются</i>

</div>

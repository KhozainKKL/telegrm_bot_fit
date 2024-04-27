<head>
    <style>
        h1, h2{
            color:green;
            font-family: 'Montserrat', sans-serif;
        }     
        .header {
            text-align: center;
        }
        img {
            height: 200px;
            width: 200px;
        }
        .query, .func {
            margin-top: 20px;
            border: 0;
            border-radius: 20px;
            padding: 0 20px 0 ;
            border-bottom: groove;
            border-top: groove;
            flex-wrap: wrap;
            place-content: center;
        }

</style>
</head>
<div class="header">
    <h1> Телеграмм бот для фитнес-клуба Loft Gym</h1>
    <img alt="лого" src="main/media/Новая папка/logo.jpg"/>
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
    <h2>Функции:</h2>
    <p>Запуск проекта через Docker</p>

```shell
  docker-compose up --build
```
<p>Запуск локального проекта на 8000 порту</p>

```shell
python manage.py runserver && python manage.py run_bot
```

</div>

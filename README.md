Ветка создана с целью развития и поддержки "Сценариев 2" (и не только) на контролерах ZONT, отсюда название ZONT_CS (custom script).

[📚 Сценарии 2 ZONT](https://docs.google.com/document/d/1n5BnrRkgcdV2D22Sd6xOP3aeWC6Px4gHgwG8sRJjgxk/edit?tab=t.0#heading=h.d04cvaqy2wsb) - дока от разработчика

 [Оффлайн редактор Zont_Scripts_Editor_v2.zip](https://drive.google.com/file/d/14QW_hGwSlc3psBsUlFrizpmjhs-m-M5P/view)

 [Progr_v1](https://drive.google.com/file/d/1JEg6Wu409BzNMZkDGUuUK4ZZP6ToX1KM/view****) - Off-line терминал с доступом к ФС (в том числе по RS485)

**[WEB редактор SCRIPTS 2](https://zse2.elifantiev.ru)** - On-line Web редактор от пользователя (Благодарность Олегу за его труд)

Раздел **[Команды](./01_Команды)** содержит управляющие команды для конфигурирования и настройки устройства через Терминал/СМС

Раздел **[Modbus](./02_Modbus)** содержит данные по работе с протоколом modbus через "сценарии 2"

Раздел **[Examples](./00_Examples)** содержит примеры, выполненные разработчиком ПО ZONT

Файл **MQTT-runn.pcl** - сценарий для загрузки и отладки объемных сценариев через MQTT (настройки MQTT выполняются в интерфейсе ZONT ЛК)

файл **utils.pcl** должен обязательно лежать в ФС контролера

**ДЛЯ КОРРЕКТНОЙ РАБОТЫ СЦЕНАРИЯ С КИРИЛЛИЦЕЙ - КОДИРОВКА ФАЙЛА ДОЛЖНА БЫТЬ WIN-1251**, для редактирования *.pcl рекомендую [VS Code](https://code.visualstudio.com/), либо [NotePad++](https://github.com/notepad-plus-plus/notepad-plus-plus/releases)

На ФС контролера загружается файл *.pcl

В Telegramm есть группа для монтажников - для добавления в группу обратитесь в ТехПоддержку ZONT

**Дополнительно для изучения:**

[📚 ZONT MQTT](https://docs.google.com/document/d/1JuJVvdGWtXVJxJox-oWP7PqfEYpra0QgJA488m3KHFw/edit?tab=t.0#heading=h.m98n6nkj4s9v)

[📚 ZONT Modbus Rtu](https://docs.google.com/document/d/1XjOHEuJpMY9IqV8XaPX0bLWLuGSE3-uRDPLUh_qEdKo/edit?tab=t.0)

[📚 ZONT WS(JSON)](https://docs.google.com/document/d/10ErPAZ_MGFeN89Erq6on2JHCHVW_1uYS8RLep1xl-ms/edit?tab=t.0)

База "Сценариев 2" выполнена на основании [Pickle](https://github.com/howerj/pickle "Перейти к почитать") с дополнительными функциями

Я не являюсь сотрудником компании Микролайн и данный проект развивается "как есть". 
Вся ответственность за использование материала из данного источника лежит на Вас

**С 573 прошивки добавлены:**

Запрос тепла к промежуточному контуру

Исполнительное устройство - ПИД регулятор

Для настройки можно посмотреть https://inner.su/services/kalkulyator-nastroyki-pid-regulyatorov/

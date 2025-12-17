
<img width="1818" height="2756" alt="2  Функция fTestTVI" src="https://github.com/user-attachments/assets/5c4e427c-9386-49ed-8406-6f4b4235a830" />
<img width="2080" height="6224" alt="1  Основной алгоритм работы системы" src="https://github.com/user-attachments/assets/0848e5e3-50c4-4897-abe9-5cfff5efdadd" />
<img width="7565" height="1577" alt="9  Полная архитектура системы" src="https://github.com/user-attachments/assets/8be5013f-cda4-4298-a02b-7dd6cc726965" />
<img width="1755" height="3267" alt="8  Алгоритм сортировки котлов от ведущего" src="https://github.com/user-attachments/assets/df174f30-6e4e-4096-bfdc-524bfad76089" />
<img width="6936" height="1323" alt="7  Логика работы с каскадом котлов" src="https://github.com/user-attachments/assets/24aebd5c-e37d-43a4-9fba-37eabfd243fd" />
<img width="1844" height="2529" alt="6  Функция fSetMask" src="https://github.com/user-attachments/assets/7d8f777f-1e85-494e-b346-22554d43faf2" />
<img width="1763" height="2722" alt="5  Функция fSetTCas " src="https://github.com/user-attachments/assets/59d50323-6c17-47b3-a6e0-d8d86470caad" />
<img width="783" height="2441" alt="4  Функция fCalcTVI " src="https://github.com/user-attachments/assets/4d2d5b60-d950-44eb-a132-2935e228a8e7" />
<img width="2471" height="1841" alt="3  Функция fCountB" src="https://github.com/user-attachments/assets/823d744b-4502-4fe1-a74f-159a01674eb7" />

Основной принцип: Система работает по таймеру (5 секунд), постоянно мониторит температуру и регулирует работу котлов.

Ключевые параметры:

TVI (Температурный Виртуальный Интеграл) - интегральный показатель

TVIm (-40) - нижний порог для увеличения котлов

TVIp (80) - верхний порог для уменьшения котлов

CountB - текущее количество работающих котлов (1-3)

Логика управления:

При низкой нагрузке (TVI < -40) - включаем дополнительный котел

При высокой нагрузке (TVI > 80) - отключаем котел

Каждый следующий котел работает с более низкой температурой

Формула уставок: Температура_котла_N = Требуемая_температура + 60 - 40*(N-1)

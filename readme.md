# Установка и настройка PostgreSQL на удалённые серверы через Ansible

## 🖥️ Описание задачи

Приложение автоматически:

- Подключается к двум удалённым серверам по SSH (один на Debian, второй на AlmaLinux)
- Измеряет нагрузку и выбирает менее загруженный хост
- Устанавливает PostgreSQL на целевом хосте
- Настраивает доступ к БД извне
- Создаёт пользователя `student` с доступом только с IP второго сервера
- Проверяет подключение к БД через `SELECT 1`

---

## ⚙️ Настройка окружения

Перед запуском я развернул 2 виртуальные машины в VirtualBox:

1. Настроил `host-only` сеть, чтобы хост мог обращаться к ВМ. Примеры IP по DHCP:
   - AlmaLinux: `192.168.56.106`
   - Debian: `192.168.56.105`

2. Настроил подключение по SSH:
   - В `/etc/ssh/sshd_config` на каждой машине:
     - Временно включил `PasswordAuthentication yes` и `PermitRootLogin yes`
     - Загрузил публичный ключ:  
       `ssh-copy-id -i ~/.ssh/ansible_key.pub root@<ip-адрес>`
     - Отключил парольную авторизацию обратно (`PasswordAuthentication no`, `PubkeyAuthentication yes`)

---

## Запуск приложения

### 1. Установка зависимостей

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Установить `ansible` используя пакетный менеджер ОС. Пример на Debian/Ubuntu:
```bash
sudo apt update
sudo apt install -y ansible
```

### 3. Команда для запускa
Приложение может принимать как ip адреса машин и так хостнейм.
```bash
sudo python3 deploy.py --key ~/.ssh/ansible_key --db_password pass123 "192.168.56.105,192.168.56.106"
```
или
```bash
chmod +x deploy.py
sudo ./deploy.py --key ~/.ssh/ansible_key --db_password pass123 "alma-vm,debian-vm"
```

### Возникшие вопросы
1. ansible не может использовать * в путях к файлам, добавил таски для динамического опредиления путей.
2. ansible выполняется на удаленных машинах черзе python и в для таски "Create user=student" пришлось установить либу python3-psycopg2
3. Чтобы проверить соединение между машинами:
   1. Создал отдельный плей с установкой psql.
   2. Создал отдельный плей для настройки фаервола(важно добавил для debian правило на 22 порт, чтобы не обрубить себе доступ).
4. Пароль от пользователя student вынес для передачи в скрипт с последующим прокидываением в ansible, чтобы не светить пароль в коде. 

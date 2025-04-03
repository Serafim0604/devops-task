## Настройка окружения 
Перед началом работы настроил 2 ВМ:
1. Добавляем host-only сеть, чтобы можно было с хоста ходить в вм. По dhcp получил IP:
   1. Alma: 192.168.56.106
   2. Debian: 192.168.56.105
   3. Прописал IP адреса в inventory.yaml

2. Добавил ssh ключи на удаленные машины:
   1. На каждой машине в файле `/etc/ssh/sshd_config` включил авторизацию по паролю(PasswordAuthentication yes) и разрешил подключение через root(PermitRootLogin yes)
   2. Для каждой машины передал ключ `ssh-copy-id -i ~/.ssh/ansible_key.pub root@{ip сервера}`
   3. На каждой машине отключил авторизацию по пароли(PasswordAuthentication no) и добавил авторизацию по ключу(PubkeyAuthentication yes)

## Запуск приложения

## Команды 
1. `ansible all -i inventory.yaml -m ping` - проверить соединение с серверами
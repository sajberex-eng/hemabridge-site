# Как обновить сайт https://bridge.hemcenter.kz/

Сайт лежит на сервере Центра гематологии (Apache, Ubuntu). Новая версия берётся с GitHub (`sajberex-eng/hemabridge-site`, ветка `hemabridge-redesign`).

## Один раз: подготовить сервер

1. Подключиться из PowerShell: `ssh ИМЯ@АДРЕС` (данные даёт админ; пароль или ключ вводится только в терминале).
2. Узнать папку сайта: `grep -ri DocumentRoot /etc/apache2/sites-enabled/` — строка с `bridge.hemcenter.kz`.
3. Скачать проект на сервер:
   ```
   git clone -b hemabridge-redesign https://github.com/sajberex-eng/hemabridge-site.git ~/hemabridge-site
   ```

## Каждый раз после правок

1. На компьютере: пересобрать (`cd src; python build.py`), закоммитить и отправить на GitHub (`git push`).
2. Обновить сервер одной командой из PowerShell:
   ```
   ssh ИМЯ@АДРЕС "bash ~/hemabridge-site/tools/deploy.sh ПАПКА_САЙТА"
   ```
   Скрипт скачивает новую версию, сохраняет копию текущего сайта в `~/hemabridge-backups/` и копирует на сайт только публичные файлы: `index.html`, `i18n/`, `img/`, `docs/`, `robots.txt`, `.htaccess`. Исходники (`src/`, `tools/`, `.git`) на сайт не попадают.
3. Открыть https://bridge.hemcenter.kz/ и проверить подпись внизу страницы: «версия …» должна совпадать с той, что в `src/build.py`.

## Откат

```
ssh ИМЯ@АДРЕС
ls ~/hemabridge-backups/
tar -xzf ~/hemabridge-backups/ДАТА.tar.gz -C ПАПКА_САЙТА
```

## Без SSH

Заархивировать `index.html`, `i18n/`, `img/`, `docs/`, `robots.txt`, `.htaccess` и загрузить в папку сайта с заменой файлов.

## Важно

- Сайт закрыт от поисковиков (`noindex` + `robots.txt`) до официального запуска. Для запуска убрать `noindex` в `src/build.py` и `Disallow` в `robots.txt`.
- Формы демонстрационные. Реальные данные пациентов можно принимать только на серверах в Казахстане.

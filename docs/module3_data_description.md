# Данные для третьего модуля

## Где находятся данные

В проекте найдены такие файлы с результатами обхода:

- `data/spbu_10/pages.json`
- `data/spbu_30/pages.json`
- `data/spbu_5000/pages.json`
- `data/spbu/pages.json`
- `data/benchmark/spbu_small/pages.json`
- `data/benchmark/spbu_medium/pages.json`

Также рядом с ними есть `pages.csv` и `report.json`. Общие результаты benchmark лежат в:

- `data/benchmark/benchmark_results.json`
- `data/benchmark/benchmark_results.csv`
- `data/benchmark/benchmark_report.md`

Папка `data/spbu/` создана отдельным запуском краулера для подготовки данных третьего модуля.

## Какие поля используются

Для построения инвертированного индекса нужны поля из `pages.json`:

- `url` - адрес страницы;
- `title` - заголовок страницы;
- `text` - очищенный текст страницы;
- `status_code` - чтобы брать только успешно загруженные страницы;
- `error` - чтобы пропускать страницы с ошибками.

В найденных файлах СПбГУ поле `text` есть. В маленьких наборах `spbu_10`, `spbu_30`, `benchmark/spbu_small` и `benchmark/spbu_medium` оно заполнено у всех страниц. В большом наборе `data/spbu_5000/pages.json` поле `text` есть у всех 2161 страниц, непустой текст есть у 2140 страниц.

В `data/spbu/pages.json` поле `text` заполнено у 50 страниц.

## Как передавать данные в модуль 3

В модуле 3 нужно читать `pages.json` и фильтровать страницы:

- `status_code == 200`;
- `error == null` или `error == ""`;
- `text` не пустой.

Для каждой подходящей страницы нужно создать документ:

- `document_id` или `doc_id` = порядковый номер или хэш URL;
- `url` = адрес страницы;
- `title` = заголовок;
- `text` = текст страницы.

Дальше поле `text` используется для токенизации и построения инвертированного индекса. Поля `url` и `title` нужны, чтобы показывать найденный документ в результатах поиска, а `status_code` и `error` нужны только на этапе отбора страниц.

## Пример формата одного документа

```json
{
  "doc_id": 1,
  "url": "https://spbu.ru/...",
  "title": "...",
  "text": "..."
}
```

## Рекомендуемый входной файл для модуля 3

- Для маленькой проверки кода: `data/benchmark/spbu_small/pages.json` или `data/spbu_10/pages.json`.
- Для среднего теста: `data/benchmark/spbu_medium/pages.json` или `data/spbu_30/pages.json`.
- Для основного индексирования СПбГУ: `data/spbu/pages.json` или `data/spbu_5000/pages.json`.

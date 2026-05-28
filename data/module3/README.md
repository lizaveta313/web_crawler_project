# Данные для модуля 3

В этой папке лежат JSONL-файлы с документами для построения инвертированного индекса.

Основные файлы:

- `spbu_documents.jsonl` - документы СПбГУ.

Файлы для быстрой проверки:

- `spbu_documents_small.jsonl`.

Каждая строка JSONL содержит `doc_id`, `url`, `title` и `text`.

Пересоздать данные можно командами:

```bash
python prepare_module3_data.py --input data/spbu/pages.json --output data/module3/spbu_documents.jsonl --min-text-length 50
```

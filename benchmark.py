"""Benchmark script for the educational web crawler."""

from __future__ import annotations

import csv
import gc
import json
import platform
import sys
import time
import tracemalloc
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from crawler.config import CrawlerConfig
from crawler.crawler import WebCrawler
from crawler.report import build_report
from crawler.storage import ResultStorage


BENCHMARK_DIR = Path("data") / "benchmark"
RESULTS_JSON = BENCHMARK_DIR / "benchmark_results.json"
RESULTS_CSV = BENCHMARK_DIR / "benchmark_results.csv"
REPORT_MD = BENCHMARK_DIR / "benchmark_report.md"

CSV_COLUMNS = [
    "scenario_name",
    "url",
    "max_pages",
    "max_depth",
    "delay",
    "processed_pages",
    "successful_pages",
    "error_pages",
    "total_links_found",
    "internal_links_total",
    "external_links_total",
    "unique_internal_links",
    "unique_external_links",
    "unique_external_resources",
    "unique_file_links_doc_docx_pdf",
    "pages_with_text",
    "total_text_length",
    "execution_time_seconds",
    "peak_memory_mb",
    "comment",
]


@dataclass(frozen=True)
class Scenario:
    name: str
    url: str
    max_pages: int
    max_depth: int
    delay: float
    output_dir: Path


SCENARIOS = [
    Scenario("spbu_small", "https://spbu.ru", 10, 1, 0.5, BENCHMARK_DIR / "spbu_small"),
    Scenario("spbu_medium", "https://spbu.ru", 30, 2, 0.5, BENCHMARK_DIR / "spbu_medium"),
]


def main() -> None:
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)

    results = [run_scenario(scenario) for scenario in SCENARIOS]
    metadata = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
    }

    save_json(results, metadata)
    save_csv(results)
    save_markdown_report(results, metadata)

    print(f"Saved: {RESULTS_CSV}")
    print(f"Saved: {RESULTS_JSON}")
    print(f"Saved: {REPORT_MD}")


def run_scenario(scenario: Scenario) -> dict[str, Any]:
    gc.collect()
    tracemalloc.start()
    start_time = time.perf_counter()
    row = empty_row(scenario, "")

    try:
        config = CrawlerConfig(
            start_url=scenario.url,
            max_pages=scenario.max_pages,
            max_depth=scenario.max_depth,
            delay=scenario.delay,
            output_dir=scenario.output_dir,
        )
        pages = WebCrawler(config).crawl()
        report = build_report(pages)

        storage = ResultStorage(scenario.output_dir)
        storage.save_pages_json(pages)
        storage.save_pages_csv(pages)
        report_path = storage.save_report_json(report)
        report_from_file = json.loads(report_path.read_text(encoding="utf-8"))

        row = row_from_report(scenario, report_from_file, build_comment(pages, report_from_file))
    except Exception as exc:
        row = empty_row(scenario, shorten(f"Ошибка запуска: {exc}"))
    finally:
        execution_time = time.perf_counter() - start_time
        _current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    row["execution_time_seconds"] = round(execution_time, 3)
    row["peak_memory_mb"] = round(peak_memory / (1024 * 1024), 3)
    return row


def row_from_report(scenario: Scenario, report: dict[str, Any], comment: str) -> dict[str, Any]:
    row = empty_row(scenario, comment)
    row.update(
        {
            "processed_pages": report.get("total_pages_processed", 0),
            "successful_pages": report.get("successful_pages", 0),
            "error_pages": report.get("error_pages", 0),
            "total_links_found": report.get("total_links_found", 0),
            "internal_links_total": report.get("internal_links_total", 0),
            "external_links_total": report.get("external_links_total", 0),
            "unique_internal_links": report.get("unique_internal_links", 0),
            "unique_external_links": report.get("unique_external_links", 0),
            "unique_external_resources": report.get("unique_external_resources", 0),
            "unique_file_links_doc_docx_pdf": report.get("unique_file_links_doc_docx_pdf", 0),
            "pages_with_text": report.get("pages_with_text", 0),
            "total_text_length": report.get("total_text_length", 0),
        }
    )
    return row


def empty_row(scenario: Scenario, comment: str) -> dict[str, Any]:
    return {
        "scenario_name": scenario.name,
        "url": scenario.url,
        "max_pages": scenario.max_pages,
        "max_depth": scenario.max_depth,
        "delay": scenario.delay,
        "processed_pages": 0,
        "successful_pages": 0,
        "error_pages": 0,
        "total_links_found": 0,
        "internal_links_total": 0,
        "external_links_total": 0,
        "unique_internal_links": 0,
        "unique_external_links": 0,
        "unique_external_resources": 0,
        "unique_file_links_doc_docx_pdf": 0,
        "pages_with_text": 0,
        "total_text_length": 0,
        "execution_time_seconds": 0,
        "peak_memory_mb": 0,
        "comment": comment,
    }


def build_comment(pages: list[Any], report: dict[str, Any]) -> str:
    first_error = next((page.error for page in pages if page.error), None)
    if report.get("successful_pages", 0) == 0 and report.get("error_pages", 0) > 0:
        return shorten(f"Страницы не загрузились: {first_error}")
    if report.get("error_pages", 0) > 0:
        return shorten(f"Есть страницы с ошибками: {first_error}")
    return "Выполнено успешно."


def shorten(text: str, limit: int = 180) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def save_json(results: list[dict[str, Any]], metadata: dict[str, str]) -> None:
    payload = {"metadata": metadata, "results": results}
    RESULTS_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_csv(results: list[dict[str, Any]]) -> None:
    with RESULTS_CSV.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(results)


def save_markdown_report(results: list[dict[str, Any]], metadata: dict[str, str]) -> None:
    lines = [
        "# Отчёт о тестировании поискового робота",
        "",
        "## Цель тестирования",
        "",
        "Проверить работу поискового робота на сайте СПбГУ с разными параметрами обхода, а также измерить время выполнения и потребление памяти.",
        "",
        "## Условия запуска",
        "",
        f"- версия Python: {metadata['python_version']};",
        f"- операционная система: {metadata['platform']};",
        "- использовались небольшие ограничения `max_pages` и `max_depth`, чтобы не делать слишком большой обход при обычном benchmark;",
        "- задержка `delay` нужна, чтобы не перегружать сайт частыми запросами;",
        "- память измерялась стандартным модулем `tracemalloc`.",
        "",
        "## Сценарии",
        "",
        "| Сценарий | Сайт | max_pages | max_depth | delay |",
        "|---|---|---:|---:|---:|",
    ]

    for row in results:
        lines.append("| {scenario_name} | {url} | {max_pages} | {max_depth} | {delay} |".format(**row))

    lines.extend(
        [
            "",
            "## Результаты",
            "",
            "| Сценарий | Обработано страниц | Найдено ссылок | Внутренних ссылок | Внешних ссылок | Страниц с ошибками | Страниц с текстом | Время, с | Память, МБ |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for row in results:
        lines.append(
            (
                "| {scenario_name} | {processed_pages} | {total_links_found} | "
                "{internal_links_total} | {external_links_total} | {error_pages} | "
                "{pages_with_text} | {execution_time_seconds:.3f} | {peak_memory_mb:.3f} |"
            ).format(**row)
        )

    comments = [row for row in results if row["comment"] and row["comment"] != "Выполнено успешно."]
    if comments:
        lines.extend(["", "## Комментарии", ""])
        for row in comments:
            lines.append(f"- {row['scenario_name']}: {row['comment']}")

    lines.extend(
        [
            "",
            "## Вывод",
            "",
            "При увеличении `max_pages` и `max_depth` время работы обычно увеличивается, потому что робот обрабатывает больше страниц. Память растёт умеренно, так как программа хранит список уже обработанных страниц и найденные ссылки. Результат зависит от структуры сайта СПбГУ. Часть ошибок может быть связана с недоступными страницами, редиректами или ограничениями сайта.",
        ]
    )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

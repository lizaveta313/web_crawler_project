import json

from prepare_module3_data import convert_pages_to_jsonl, prepare_documents


def make_pages() -> list[dict[str, object]]:
    return [
        {
            "url": "https://example.com/ok",
            "status_code": 200,
            "title": "Ok",
            "depth": 0,
            "text": " Useful text long enough for module three indexing and search tests ",
            "internal_links": [],
            "external_links": [],
            "error": "",
        },
        {
            "url": "https://example.com/error",
            "status_code": 200,
            "title": "Error",
            "depth": 1,
            "text": "Text with error long enough for module three indexing",
            "internal_links": [],
            "external_links": [],
            "error": "Request failed",
        },
        {
            "url": "https://example.com/empty",
            "status_code": 200,
            "title": "Empty",
            "depth": 1,
            "text": "   ",
            "internal_links": [],
            "external_links": [],
            "error": "",
        },
        {
            "url": "https://example.com/status",
            "status_code": 500,
            "title": "Status",
            "depth": 1,
            "text": "Server error text long enough for module three indexing",
            "internal_links": [],
            "external_links": [],
            "error": "",
        },
        {
            "url": "https://example.com/ok-2",
            "status_code": 200,
            "title": "Ok 2",
            "depth": 1,
            "text": "Second useful text long enough for module three indexing",
            "internal_links": [],
            "external_links": [],
            "error": None,
        },
    ]


def test_prepare_documents_filters_errors_empty_text_and_bad_status() -> None:
    documents = prepare_documents(make_pages())

    assert [document["url"] for document in documents] == [
        "https://example.com/ok",
        "https://example.com/ok-2",
    ]


def test_prepare_documents_sets_sequential_doc_ids() -> None:
    documents = prepare_documents(make_pages())

    assert [document["doc_id"] for document in documents] == [1, 2]


def test_prepare_documents_respects_limit() -> None:
    documents = prepare_documents(make_pages(), limit=1)

    assert len(documents) == 1
    assert documents[0]["doc_id"] == 1


def test_prepare_documents_skips_short_text() -> None:
    pages = make_pages()
    pages.append(
        {
            "url": "https://example.com/short",
            "status_code": 200,
            "title": "Short",
            "depth": 1,
            "text": "too short",
            "internal_links": [],
            "external_links": [],
            "error": "",
        }
    )

    documents = prepare_documents(pages, min_text_length=50)

    assert "https://example.com/short" not in [document["url"] for document in documents]


def test_convert_pages_to_jsonl_creates_file(tmp_path) -> None:
    input_path = tmp_path / "pages.json"
    output_path = tmp_path / "module3" / "documents.jsonl"
    input_path.write_text(json.dumps(make_pages()), encoding="utf-8")

    stats = convert_pages_to_jsonl(input_path, output_path)

    assert stats["total_pages_read"] == 5
    assert stats["documents_saved"] == 2
    assert stats["skipped_pages"] == 3
    assert output_path.exists()

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {
        "doc_id": 1,
        "url": "https://example.com/ok",
        "title": "Ok",
        "text": "Useful text long enough for module three indexing and search tests",
    }

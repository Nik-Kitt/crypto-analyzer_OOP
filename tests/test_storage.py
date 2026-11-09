import pytest
import json


from storage import JsonStorage, BaseStorage


@pytest.fixture
def storage():
    return JsonStorage()


@pytest.fixture
def results():
    return {
        'generated_at': '2026-11-02 12:00:00',
        'total_coins_analyzed': 2,
    }


def test_base_storage_is_abstract():
    with pytest.raises(TypeError):
        BaseStorage()  # type: ignore[abstract]


def test_json_storage_init_invalid_filename():
    with pytest.raises(TypeError):
        JsonStorage(name_file=123)  # type: ignore[arg-type]


def test_main_saves_report_to_storage(storage):
    assert storage.name_file == 'crypto_report.json'


def test_json_storage_save(results, tmp_path):
    file_path = tmp_path / 'test_storage.json'
    storage = JsonStorage(name_file=str(file_path))
    storage.save(results)
    with open(file_path, encoding='utf-8') as file:
        result_data = json.load(file)
    assert result_data == results

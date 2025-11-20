from types import SimpleNamespace

import pytest
from datasets import Features
from PIL import Image as PILImage

from modelhub.clients.dataset_client import DatasetClient


def make_client():
    """Create a DatasetClient instance without running BaseClient.__init__.

    We use __new__ and then set attributes that DatasetClient methods expect.
    """
    client = DatasetClient.__new__(DatasetClient)
    # Provide simple placeholders for HTTP helpers used in tests
    client.get = lambda endpoint, **kwargs: {}
    client.post = lambda endpoint, **kwargs: {}
    client.client = SimpleNamespace(
        get=lambda url: SimpleNamespace(
            content=b"", text="", raise_for_status=lambda: None
        )
    )
    return client


def test_list_and_get_dataset():
    c = make_client()

    c.get = lambda endpoint: {"data": [{"id": "d1", "name": "dataset-a"}]}
    assert c.list_datasets() == [{"id": "d1", "name": "dataset-a"}]

    c.get = lambda endpoint: {"data": {"id": "d2", "name": "dataset-b"}}
    assert c.get_dataset_by_name("dataset-b") == {"id": "d2", "name": "dataset-b"}


def test_get_dataset_versions():
    c = make_client()
    c.get = lambda endpoint: {
        "data": {"versions": [{"version_id": 1}, {"version_id": 2}]}
    }
    assert c.get_dataset_versions("d1") == [{"version_id": 1}, {"version_id": 2}]


def test_get_version_files_variants():
    c = make_client()

    # Variant: response['data']['files']
    c.get = lambda endpoint: {"data": {"files": ["a", "b"]}}
    assert c.get_version_files("d", 1) == ["a", "b"]

    # Variant: response['data'] is list
    c.get = lambda endpoint: {"data": ["c"]}
    assert c.get_version_files("d", 1) == ["c"]

    # Variant: response is list
    c.get = lambda endpoint: ["d"]
    assert c.get_version_files("d", 1) == ["d"]

    # Unexpected format -> returns []
    c.get = lambda endpoint: {"unexpected": True}
    assert c.get_version_files("d", 1) == []


def test_get_signed_url_read_and_upload():
    c = make_client()

    def post_read(endpoint, json=None):
        return {"data": {"signedUrl": f"read://{json.get('file_path')}"}}

    def post_upload(endpoint, json=None):
        return {"data": {"signedUrl": f"upload://{json.get('file_path')}"}}

    c.post = post_read
    assert (
        c.get_signed_url("did", "path/to/file.txt", 1, is_read=True)
        == "read://path/to/file.txt"
    )

    c.post = post_upload
    assert (
        c.get_signed_url("did", "path/to/file.txt", None, is_read=False)
        == "upload://path/to/file.txt"
    )


def test_get_file_extension():
    c = make_client()
    assert c.get_file_extension("https://host/path/file.csv") == ".csv"
    assert c.get_file_extension("/local/path/image.PNG") == ".png"


def test_normalize_json_data():
    c = make_client()
    # list -> return as-is
    data = [1, 2, 3]
    assert c._normalize_json_data(data, "url") == data

    # dict with container
    data = {"data": [{"a": 1}, {"a": 2}]}
    assert c._normalize_json_data(data, "u") == [{"a": 1}, {"a": 2}]

    # single dict
    data = {"x": 1}
    assert c._normalize_json_data(data, "u") == [{"x": 1}]

    # other
    data = "raw"
    res = c._normalize_json_data(data, "u")
    assert isinstance(res, list) and res[0]["file_path"] == "u"


def test_infer_features_and_check_nested_directories():
    c = make_client()

    img = PILImage.new("RGB", (2, 2))
    example = {
        "img": img,
        "labels": ["a", "b"],
        "numbers": [1, 2],
        "score": 1.2,
        "flag": True,
        "id": 5,
        "text": "hello",
    }

    features = c._infer_features(example)
    assert isinstance(features, Features)
    # Check keys exist
    for k in example.keys():
        assert k in features

    # check nested directories
    files = [
        {"file_path": "root/dir/split/train/file.csv"},
        {"file_path": "root/other/split/val/f.txt"},
    ]
    nested = c._check_nested_directories(files)
    assert isinstance(nested, list) and all(isinstance(x, str) for x in nested)


def test_collect_split_file_urls_basic():
    c = make_client()

    # Provide version files with top-level prefix followed by split and file
    version_files = [
        "root/train/file1.csv",
        "root/val/file2.csv",
        "root/test/file3.csv",
    ]

    c.get_version_files = lambda dataset_id, version_id: version_files
    c.get_signed_url = (
        lambda dataset_id, file_path, version_id: f"https://signed/{file_path}"
    )

    grouped = c._collect_split_file_urls("did", 1, split=None, directory=None)
    assert set(grouped.keys()) == {"train", "val", "test"}
    for k, v in grouped.items():
        assert all(u.startswith("https://signed/") for u in v)

    # request a missing split -> should raise
    with pytest.raises(ValueError):
        c._collect_split_file_urls("did", 1, split="nonexistent", directory=None)


from unittest.mock import MagicMock

import pytest

from modelhub.clients.dataset_client import DatasetClient
from modelhub.core import ModelhubCredential


@pytest.fixture
def mock_credential():
    credential = MagicMock(spec=ModelhubCredential)
    credential.get_token.return_value = "dummy-token"
    credential._modelhub_url = "http://dummy"
    return credential


@pytest.fixture
def dataset_client(mock_credential):
    client = DatasetClient(credential=mock_credential, client_id="1")
    return client


# ---------------------- Basic API Methods ---------------------- #
def test_list_datasets(monkeypatch, dataset_client):
    fake_data = [{"id": "1", "name": "dataset1"}, {"id": "2", "name": "dataset2"}]
    monkeypatch.setattr(
        dataset_client,
        "get",
        lambda endpoint, **kwargs: (
            {"data": fake_data} if endpoint == "datasets" else {}
        ),
    )
    result = dataset_client.list_datasets()
    assert result == fake_data


def test_get_dataset_by_name(monkeypatch, dataset_client):
    fake_dataset = {"id": "1", "name": "dataset1", "versions": []}
    monkeypatch.setattr(
        dataset_client,
        "get",
        lambda endpoint, **kwargs: (
            {"data": fake_dataset} if endpoint == "datasets/dataset1" else {}
        ),
    )
    result = dataset_client.get_dataset_by_name("dataset1")
    assert result == fake_dataset


def test_get_dataset_versions(monkeypatch, dataset_client):
    fake_versions = [{"version_id": 1}, {"version_id": 2}]
    monkeypatch.setattr(
        dataset_client,
        "get",
        lambda endpoint, **kwargs: (
            {"data": {"versions": fake_versions}} if endpoint == "datasets/1" else {}
        ),
    )
    result = dataset_client.get_dataset_versions("1")
    assert result == fake_versions


def test_get_signed_url(monkeypatch, dataset_client):
    fake_signed_url = "http://signed.url"
    monkeypatch.setattr(
        dataset_client,
        "post",
        lambda endpoint, json, **kwargs: {"data": {"signedUrl": fake_signed_url}},
    )
    result = dataset_client.get_signed_url("1", "file.csv", version=1, is_read=True)
    assert result == fake_signed_url


# ---------------------- load_dataset Tests ---------------------- #
def test_load_dataset_multiple_nested_directories(monkeypatch, dataset_client):
    fake_dataset = {
        "id": "1",
        "versions": [
            {
                "version_id": 1,
                "files": [
                    {"file_path": "data1/splitA/file1.csv"},
                    {"file_path": "data2/splitA/file2.csv"},
                ],
            }
        ],
    }
    monkeypatch.setattr(
        dataset_client, "get_dataset_by_name", lambda name: fake_dataset
    )
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    monkeypatch.setattr(
        dataset_client,
        "_load_dataset_by_format",
        lambda split_file_urls: split_file_urls,
    )
    with pytest.raises(ValueError, match="Multiple nested directories found"):
        dataset_client.load_dataset("dataset1")


def test_load_dataset_success(monkeypatch, dataset_client):
    fake_dataset = {
        "id": "1",
        "versions": [
            {
                "version_id": 1,
                "files": [
                    {"file_path": "dir/splitA/file1.csv"},
                    {"file_path": "dir/splitA/file2.csv"},
                ],
            }
        ],
    }
    monkeypatch.setattr(
        dataset_client, "get_dataset_by_name", lambda name: fake_dataset
    )
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    monkeypatch.setattr(
        dataset_client,
        "_load_dataset_by_format",
        lambda split_file_urls: split_file_urls,
    )
    # Prevent real HTTP calls by mocking get_version_files
    version_files = ["dir/splitA/file1.csv", "dir/splitA/file2.csv"]
    monkeypatch.setattr(
        dataset_client,
        "get_version_files",
        lambda dataset_id, version_id: version_files,
    )
    result = dataset_client.load_dataset("dataset1", directory="dir")
    # Note: implementation strips the first path component before calling get_signed_url,
    # so signed URLs will not include the original top-level directory.
    expected = {"splitA": ["signed_splitA/file1.csv", "signed_splitA/file2.csv"]}
    assert result == expected


def test_load_dataset_default_version(monkeypatch, dataset_client):
    fake_dataset = {
        "id": "1",
        "versions": [
            {
                "version_id": 2,
                "files": [{"file_path": "dir/splitA/file1.csv"}],
            },
            {
                "version_id": 1,
                "files": [{"file_path": "dir/splitA/oldfile.csv"}],
            },
        ],
    }
    monkeypatch.setattr(
        dataset_client, "get_dataset_by_name", lambda name: fake_dataset
    )
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    monkeypatch.setattr(
        dataset_client,
        "_load_dataset_by_format",
        lambda split_file_urls: split_file_urls,
    )
    # Mock get_version_files to avoid network calls
    version_files = ["dir/splitA/file1.csv"]
    monkeypatch.setattr(
        dataset_client,
        "get_version_files",
        lambda dataset_id, version_id: version_files,
    )
    result = dataset_client.load_dataset("dataset1", directory="dir")
    expected = {"splitA": ["signed_splitA/file1.csv"]}
    assert result == expected


def test_load_dataset_version_not_found(monkeypatch, dataset_client):
    fake_dataset = {
        "id": "1",
        "versions": [{"version_id": 1, "files": []}, {"version_id": 2, "files": []}],
    }
    monkeypatch.setattr(
        dataset_client, "get_dataset_by_name", lambda name: fake_dataset
    )
    with pytest.raises(ValueError, match="Version 3 not found for dataset dataset1"):
        dataset_client.load_dataset("dataset1", version=3)


# ---------------------- Internal Helper Methods ---------------------- #
def test__check_nested_directories(dataset_client):
    files = [
        {"file_path": "dir/splitA/file1.csv"},
        {"file_path": "dir/subdir/splitB/file2.csv"},
    ]
    result = dataset_client._check_nested_directories(files)
    expected = ["dir", "dir/subdir"]
    assert set(result) == set(expected)


def test_get_file_extension(dataset_client):
    url = "http://example.com/file.csv"
    ext = dataset_client.get_file_extension(url)
    assert ext == ".csv"


def test__collect_split_file_urls(monkeypatch, dataset_client):
    files = [
        {"file_path": "dir/splitA/file1.csv", "version_id": 1},
        {"file_path": "dir/splitA/file2.csv", "version_id": 1},
        {"file_path": "dir/splitB/file3.csv", "version_id": 1},
    ]
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    # Mock get_version_files to return simple path list
    monkeypatch.setattr(
        dataset_client,
        "get_version_files",
        lambda dataset_id, version_id: [f["file_path"] for f in files],
    )
    result = dataset_client._collect_split_file_urls(
        "dataset1", 1, split=None, directory="dir"
    )
    assert set(result.keys()) == {"splitA", "splitB"}
    # Only splitA and splitB should appear
    # Note: _collect_split_file_urls depends on get_version_files in real code; here we simulate minimal behavior
    # This test mainly ensures function runs; detailed logic covered in load_dataset tests


# ---------------------- Image Dataset Tests ---------------------- #
def test__load_image_dataset(monkeypatch, dataset_client):
    # Mock response
    mock_response = MagicMock()
    mock_response.content = b"fake_image_content"
    mock_response.raise_for_status = MagicMock()

    # Mock image
    mock_img = MagicMock()
    mock_img.mode = "RGB"
    mock_img.convert = MagicMock(return_value=mock_img)

    # Patch http get and PIL
    monkeypatch.setattr(dataset_client.client, "get", lambda url: mock_response)
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.PILImage.open", lambda io_bytes: mock_img
    )
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.io.BytesIO", lambda content: b"fake_bytes_io"
    )

    # Patch Dataset.from_dict and DatasetDict
    mock_dataset = MagicMock()
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.Dataset.from_dict",
        lambda data, features=None: mock_dataset,
    )
    mock_dataset_dict = MagicMock()
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.DatasetDict",
        lambda datasets: mock_dataset_dict,
    )

    split_file_urls = {"train": ["http://example.com/img1.png"]}
    result = dataset_client._load_image_dataset(split_file_urls)
    assert result == mock_dataset_dict


def test__load_image_dataset_error_handling(monkeypatch, dataset_client):
    mock_logger = MagicMock()
    monkeypatch.setattr("modelhub.clients.dataset_client.logger", mock_logger)

    def mock_get(url):
        if "bad" in url:
            raise Exception("Failed to load")
        mock_resp = MagicMock()
        mock_resp.content = b"img_content"
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    monkeypatch.setattr(dataset_client.client, "get", mock_get)
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.PILImage.open",
        lambda io_bytes: MagicMock(mode="RGB"),
    )
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.io.BytesIO", lambda content: b"fake"
    )
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.Dataset.from_dict",
        lambda data, features=None: MagicMock(),
    )
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.DatasetDict", lambda datasets: MagicMock()
    )

    split_file_urls = {
        "train": ["http://example.com/good.png", "http://example.com/bad.png"]
    }
    dataset_client._load_image_dataset(split_file_urls)
    mock_logger.error.assert_called_once()


# ---------------------- _load_dataset_by_format ---------------------- #
def test__load_dataset_by_format_unsupported(monkeypatch, dataset_client):
    split_file_urls = {"train": ["http://example.com/file.unsupported"]}
    with pytest.raises(ValueError, match="Unsupported file format"):
        dataset_client._load_dataset_by_format(split_file_urls)

import io
import os
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from datasets import Dataset, DatasetDict, Features, Image, Sequence, Value
from datasets import load_dataset as hf_load_dataset
from PIL import Image as PILImage
from tqdm.auto import tqdm

from ..core import BaseClient
from ..utils import setup_logger

logger = setup_logger(__name__)


class DatasetClient(BaseClient):
    """Client for interacting with datasets with HuggingFace-like functionality."""

    def list_datasets(self) -> List[Dict[str, Any]]:
        """
        List all available datasets.

        Returns:
            List[Dict[str, Any]]: A list of available datasets.
        """
        response = self.get("datasets")
        return response["data"]

    def get_dataset_by_name(self, dataset_name: str) -> Dict[str, Any]:
        """
        Get a dataset by name.

        Args:
            dataset_name (str): The name of the dataset.

        Returns:
            Dict[str, Any]: The dataset.
        """
        response = self.get(f"datasets/{dataset_name}")
        return response["data"]

    def get_dataset_versions(self, dataset_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a specific dataset.

        Args:
            dataset_id (str): The ID of the dataset.

        Returns:
            List[Dict[str, Any]]: A list of dataset versions.
        """
        response = self.get(f"datasets/{dataset_id}")
        return response["data"]["versions"]

    def get_version_files(self, dataset_id: str, version: int) -> List[str]:
        """
        Get all files of a specific dataset version.

        Args:
            dataset_id (str): The ID of the dataset.
            version (int): The version identifier.

        Returns:
            List[str]: A list of file paths in the dataset version.
        """
        response = self.get(f"datasets/{dataset_id}/files/{version}")

        # Handle the actual API response structure
        if isinstance(response, dict) and "data" in response:
            if isinstance(response["data"], dict) and "files" in response["data"]:
                return response["data"]["files"]
            elif isinstance(response["data"], list):
                return response["data"]
        elif isinstance(response, list):
            return response

        # Fallback for unexpected structures
        else:
            # Log the unexpected response for debugging
            print(f"Unexpected response format: {response}")
            return []

    def get_signed_url(
        self,
        dataset_id: str,
        file_path: str,
        version: Optional[int],
        is_read: bool = True,
    ) -> str:
        """
        Get a signed URL for a file.

        Args:
            file_path (str): The path to the file.
            is_read (bool): Whether the URL is for reading. Defaults to True.
            dataset_id (str): The ID of the dataset.
            version (int): The version of the file.

        Returns:
            str: The signed URL.
        """
        body = {"file_path": file_path}
        if version:
            body["version_id"] = version

        endpoint = (
            f"datasets/{dataset_id}/signedurl/read"
            if is_read
            else f"datasets/{dataset_id}/signedurl/upload"
        )
        response = self.post(endpoint, json=body)
        return response["data"]["signedUrl"]

    def load_dataset(
        self,
        dataset_name: str,
        version: Optional[int] = None,
        split: Optional[str] = None,
        directory: Optional[str] = None,
    ) -> Union[Dataset, DatasetDict]:
        """
        Load a dataset by name and version. Returns Dataset if split is specified,
        DatasetDict otherwise.

        Args:
            dataset_name (str): The name of the dataset.
            version (int, optional): The version of the dataset. Defaults to None (latest).
            split (str, optional): The split of the dataset. If specified, returns Dataset instead of DatasetDict.
            directory (str, optional): The directory path to the dataset. Defaults to None.

        Returns:
            Union[Dataset, DatasetDict]: The loaded dataset. Returns Dataset if split is specified,
                                         DatasetDict otherwise.
        """
        try:
            dataset = self.get_dataset_by_name(dataset_name)
            versions = dataset["versions"]

            if version:
                version_data = next(
                    (v for v in versions if v["version_id"] == version), None
                )
            else:
                version_data = versions[0]  # Default to latest version

            if not version_data:
                raise ValueError(
                    f"Version {version} not found for dataset {dataset_name}."
                )

            # Check for nested directories
            nested_directories = self._check_nested_directories(version_data["files"])
            if nested_directories and not directory:
                raise ValueError(
                    f"Multiple nested directories found: {nested_directories}. "
                    f"Please specify a directory path."
                )

            # Collect file URLs and determine splits
            split_file_urls = self._collect_split_file_urls(
                dataset["id"],
                version_data["version_id"],
                split=split,
                directory=directory,
            )

            logger.info("Loading dataset with splits: %s", list(split_file_urls.keys()))

            # Load dataset
            dataset_dict = self._load_dataset_by_format(split_file_urls)

            # Return Dataset if split specified.
            if split:
                if split not in dataset_dict:
                    raise ValueError(
                        f"Split '{split}' not found. Available splits: {list(dataset_dict.keys())}"
                    )
                return dataset_dict[split]

            return dataset_dict

        except Exception as e:
            logger.error(f"Error loading dataset {dataset_name}: {e}")
            raise

    def _load_dataset_by_format(
        self, split_file_urls: Dict[str, List[str]]
    ) -> DatasetDict:
        """
        Load a dataset from file URLs.

        Args:
            split_file_urls (Dict[str, List[str]]):
                A dictionary where keys are split names and values are lists of file URLs.

        Returns:
            DatasetDict: The loaded dataset.
        """
        data_files = split_file_urls
        file_extensions = [
            self.get_file_extension(file)
            for files in split_file_urls.values()
            for file in files
        ]

        # Define supported formats
        supported_formats = [
            ".csv",
            ".json",
            ".parquet",
            ".txt",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
        ]

        # Check if all extensions are supported
        unsupported_extensions = [
            ext for ext in file_extensions if ext not in supported_formats
        ]
        if unsupported_extensions:
            unique_unsupported = list(set(unsupported_extensions))
            raise ValueError(
                f"Unsupported file format: {', '.join(unique_unsupported)}. "
                f"Supported formats are: {', '.join(supported_formats)}"
            )

        # Use HuggingFace native loaders for uniform formats
        if all(ext == ".csv" for ext in file_extensions):
            logger.info("Loading CSV dataset.")
            return hf_load_dataset("csv", data_files=data_files)

        elif all(ext == ".json" for ext in file_extensions):
            logger.info("Loading JSON dataset.")
            return hf_load_dataset("json", data_files=data_files)

        elif all(ext == ".parquet" for ext in file_extensions):
            logger.info("Loading Parquet dataset.")
            return hf_load_dataset("parquet", data_files=data_files)

        elif all(ext == ".txt" for ext in file_extensions):
            logger.info("Loading text dataset.")
            return hf_load_dataset("text", data_files=data_files)

        elif all(
            ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp"] for ext in file_extensions
        ):
            logger.info("Loading image dataset...")
            return self._load_image_dataset(split_file_urls)

        # Handle mixed formats or special cases
        else:
            logger.info("Loading dataset with mixed formats manually...")
            return self._load_mixed_format_dataset(split_file_urls)

    def _load_mixed_format_dataset(
        self, split_file_urls: Dict[str, List[str]]
    ) -> DatasetDict:
        """
        Load dataset with mixed formats or formats requiring special handling.

        Args:
            split_file_urls (Dict[str, List[str]]): Split file URLs.

        Returns:
            DatasetDict: The loaded dataset.
        """
        datasets_dict = {}

        for split_name, urls in split_file_urls.items():
            logger.info(f"Processing {split_name} split with {len(urls)} files")

            all_data = []

            for url in tqdm(urls, desc=f"Loading {split_name}", unit="file"):
                try:
                    response = self.client.get(url)
                    response.raise_for_status()

                    file_extension = self.get_file_extension(url)

                    # Process different file types
                    if file_extension == ".json":
                        data = response.json()
                        normalized = self._normalize_json_data(data, url)
                        all_data.extend(normalized)

                    elif file_extension == ".jsonl":
                        # Newline-delimited JSON
                        import json

                        lines = response.text.strip().split("\n")
                        for line in lines:
                            if line.strip():
                                all_data.append(json.loads(line))

                    elif file_extension == ".csv":
                        import pandas as pd

                        df = pd.read_csv(io.StringIO(response.text))
                        all_data.extend(df.to_dict("records"))

                    elif file_extension == ".parquet":
                        import pandas as pd
                        import pyarrow.parquet as pq

                        parquet_data = pq.read_table(io.BytesIO(response.content))
                        all_data.extend(parquet_data.to_pandas().to_dict("records"))

                    elif file_extension in [".txt", ".text"]:
                        lines = response.text.split("\n")
                        for line in lines:
                            if line.strip():
                                all_data.append({"text": line.strip()})

                    elif file_extension in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
                        img = PILImage.open(io.BytesIO(response.content))
                        if img.mode == "RGBA":
                            img = img.convert("RGB")
                        all_data.append({"image": img, "file_path": url})

                    else:
                        logger.warning(f"Unsupported file format: {file_extension}")
                        all_data.append(
                            {"file_path": url, "content": response.text[:1000]}
                        )

                except Exception as e:
                    logger.error(f"Error processing file {url}: {e}")
                    continue

            # Create dataset from loaded data
            if all_data:
                features = self._infer_features(all_data[0]) if all_data else None
                datasets_dict[split_name] = Dataset.from_list(
                    all_data, features=features
                )
                logger.info(
                    f"✅ Loaded {split_name} split with {len(all_data)} examples"
                )
            else:
                logger.warning(f"⚠️ No data loaded for {split_name} split")
                datasets_dict[split_name] = Dataset.from_dict({"file_path": urls})

        return DatasetDict(datasets_dict)

    def _load_image_dataset(self, split_file_urls: Dict[str, List[str]]) -> DatasetDict:
        """
        Load image dataset by fetching and decoding the images.

        Args:
            split_file_urls (Dict[str, List[str]]): Split names to image URLs mapping.

        Returns:
            DatasetDict: Dataset containing the loaded images.
        """
        datasets_dict = {}

        for split_name, urls in split_file_urls.items():
            logger.info(f"Loading {len(urls)} images for split {split_name}")

            features = Features({"image": Image(), "file_path": Value("string")})

            images = []
            file_paths = []

            for url in tqdm(urls, desc=f"Loading {split_name} images", unit="image"):
                try:
                    response = self.client.get(url)
                    response.raise_for_status()

                    img = PILImage.open(io.BytesIO(response.content))
                    if img.mode == "RGBA":
                        img = img.convert("RGB")

                    images.append(img)
                    file_paths.append(url)

                except Exception as e:
                    logger.error(f"Error loading image from {url}: {e}")

            dataset = Dataset.from_dict(
                {"image": images, "file_path": file_paths}, features=features
            )
            datasets_dict[split_name] = dataset
            logger.info(f"✅ Loaded {len(images)} images for {split_name}")

        return DatasetDict(datasets_dict)

    def _infer_features(self, example: Dict[str, Any]) -> Features:
        """
        Infer dataset features from an example.

        Args:
            example (Dict[str, Any]): A sample data example.

        Returns:
            Features: Inferred features.
        """
        feature_dict = {}

        for key, value in example.items():
            if isinstance(value, PILImage.Image):
                feature_dict[key] = Image()
            elif isinstance(value, list):
                if value and isinstance(value[0], str):
                    feature_dict[key] = Sequence(Value("string"))
                elif value and isinstance(value[0], int):
                    feature_dict[key] = Sequence(Value("int64"))
                elif value and isinstance(value[0], float):
                    feature_dict[key] = Sequence(Value("float64"))
                else:
                    feature_dict[key] = Sequence(Value("string"))
            elif isinstance(value, int):
                feature_dict[key] = Value("int64")
            elif isinstance(value, float):
                feature_dict[key] = Value("float64")
            elif isinstance(value, bool):
                feature_dict[key] = Value("bool")
            else:
                feature_dict[key] = Value("string")

        return Features(feature_dict)

    def _normalize_json_data(self, data: Any, url: str) -> List[Dict[str, Any]]:
        """
        Normalize JSON data into a list of examples.

        Args:
            data: The parsed JSON data.
            url: The source URL for context.

        Returns:
            List[Dict[str, Any]]: Normalized data examples.
        """
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Look for common data container keys
            data_keys = ["data", "examples", "items", "records", "samples", "rows"]
            for key in data_keys:
                if key in data and isinstance(data[key], list):
                    return data[key]
            # Treat as single example
            return [data]
        else:
            return [{"value": data, "file_path": url}]

    def _collect_split_file_urls(
        self,
        dataset_id: str,
        version_id: int,
        split: Optional[str],
        directory: Optional[str],
    ) -> Dict[str, List[str]]:
        """
        Collect file URLs categorized by splits based on folder names.
        """
        split_file_urls = {}

        version_files = self.get_version_files(dataset_id, version_id)
        for path in version_files:
            # Check directory filter BEFORE removing prefix
            if directory and not path.startswith(directory):
                continue

            # NOW remove the directory prefix
            parts = path.split("/")
            file_path = "/".join(parts[1:])  # Remove first part (e.g., "dir")

            # Extract the split name from the file path
            path_parts = file_path.split("/")

            if len(path_parts) >= 3:
                split_name = path_parts[-2] if directory else path_parts[-3]
            elif len(path_parts) == 2:
                split_name = path_parts[-2]
            elif len(path_parts) == 1:
                split_name = path_parts[0].split(".")[0]
            else:
                split_name = "unknown"

            if split and split != split_name:
                continue

            if split_name not in split_file_urls:
                split_file_urls[split_name] = []

            split_file_urls[split_name].append(
                self.get_signed_url(dataset_id, file_path, version_id)
            )

        if split and split not in split_file_urls:
            available_splits = list(split_file_urls.keys())
            raise ValueError(
                f"Split '{split}' not found in the dataset. "
                f"Available splits: {available_splits}"
            )

        return split_file_urls

    def _check_nested_directories(self, files: List[Dict[str, Any]]) -> List[str]:
        """
        Check for nested directories up to the split level.

        Args:
            files (List[Dict[str, Any]]): List of file metadata.

        Returns:
            List[str]: A list of nested directories.
        """
        nested_directories = set()
        for file in files:
            nested_directory = "/".join(file["file_path"].split("/")[:-2])
            if nested_directory:
                nested_directories.add(nested_directory)
        return list(nested_directories)

    def get_file_extension(self, file_url: str) -> str:
        """
        Extract the file extension from a URL.

        Args:
            file_url (str): The file URL.

        Returns:
            str: The file extension.
        """
        path = urlparse(file_url).path
        return os.path.splitext(path)[1].lower()

    def get_dataset_info(self, dataset_name: str) -> Dict[str, Any]:
        """
        Get metadata and information about a dataset (similar to HuggingFace).

        Args:
            dataset_name (str): Name of the dataset.

        Returns:
            Dict[str, Any]: Dataset information including description, features, splits.
        """
        try:
            dataset = self.get_dataset_by_name(dataset_name)

            info = {
                "name": dataset.get("name"),
                "id": dataset.get("id"),
                "description": dataset.get("description", ""),
                "versions": [v["version_id"] for v in dataset.get("versions", [])],
                "latest_version": (
                    dataset.get("versions", [{}])[0].get("version_id")
                    if dataset.get("versions")
                    else None
                ),
            }

            # Get splits info from latest version
            if dataset.get("versions"):
                version_files = self.get_version_files(
                    dataset["id"], dataset["versions"][0]["version_id"]
                )
                splits = set()
                for path in version_files:
                    parts = path.split("/")
                    if len(parts) >= 2:
                        splits.add(parts[-2])
                info["splits"] = list(splits)

            return info

        except Exception as e:
            logger.error(f"Error getting dataset info for {dataset_name}: {e}")
            raise

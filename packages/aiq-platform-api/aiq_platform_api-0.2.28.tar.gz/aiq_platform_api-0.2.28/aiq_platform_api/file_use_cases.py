# File endpoint use cases: upload, fetch metadata, download via URL.
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Optional

import httpx

from aiq_platform_api.common_utils import AttackIQLogger, AttackIQRestClient, FileUploadUtils
from aiq_platform_api.env import ATTACKIQ_PLATFORM_API_TOKEN, ATTACKIQ_PLATFORM_URL

logger = AttackIQLogger.get_logger(__name__)


def upload_text_file(client: AttackIQRestClient, file_name: str, content: str) -> dict:
    logger.info(f"Uploading file {file_name}")
    return FileUploadUtils.upload_script_file(
        client=client,
        file_name=file_name,
        file_content=content.encode(),
        content_type="text/plain",
    )


def get_file_metadata(client: AttackIQRestClient, file_id: str) -> dict:
    meta = FileUploadUtils.get_file_metadata(client, file_id)
    logger.info(f"Retrieved metadata for file {file_id}")
    return meta


def download_file(meta: dict, destination: Optional[str] = None) -> Path:
    file_url = meta["file"]
    parsed_name = Path(httpx.URL(file_url).path).name
    target_path = Path(destination) if destination else Path(parsed_name)
    if target_path.is_dir():
        target_path = target_path / parsed_name
    logger.info(f"Downloading file to {target_path}")
    with httpx.stream("GET", file_url, timeout=60.0) as response:
        response.raise_for_status()
        target_path.write_bytes(response.read())
    return target_path.resolve()


def test_upload_and_get_metadata(client: AttackIQRestClient):
    result = upload_text_file(client, "file_use_case_test.txt", "Hello from file_use_cases")
    file_id = result["id"]
    meta = get_file_metadata(client, file_id)
    logger.info(f"File path: {result['file_path']}")
    logger.info(f"Metadata keys: {list(meta.keys())}")
    return file_id


def test_download_file(client: AttackIQRestClient, destination: Optional[str] = None):
    result = upload_text_file(client, "file_use_case_download.txt", "Download use case")
    meta = get_file_metadata(client, result["id"])
    path = download_file(meta, destination)
    logger.info(f"Downloaded file size: {os.path.getsize(path)} bytes")


def run_test(choice: "TestChoice", client: AttackIQRestClient):
    functions = {
        TestChoice.UPLOAD_AND_METADATA: lambda: test_upload_and_get_metadata(client),
        TestChoice.DOWNLOAD_FILE: lambda: test_download_file(client),
    }
    func = functions.get(choice)
    if func:
        func()
    else:
        logger.error(f"Unknown test choice: {choice}")


if __name__ == "__main__":
    if not ATTACKIQ_PLATFORM_URL or not ATTACKIQ_PLATFORM_API_TOKEN:
        logger.error("Missing ATTACKIQ_PLATFORM_URL or ATTACKIQ_PLATFORM_API_TOKEN")
        sys.exit(1)

    class TestChoice(Enum):
        UPLOAD_AND_METADATA = "upload_and_metadata"
        DOWNLOAD_FILE = "download_file"

    client = AttackIQRestClient(ATTACKIQ_PLATFORM_URL, ATTACKIQ_PLATFORM_API_TOKEN)

    choice = TestChoice.UPLOAD_AND_METADATA
    # choice = TestChoice.DOWNLOAD_FILE

    run_test(choice, client)

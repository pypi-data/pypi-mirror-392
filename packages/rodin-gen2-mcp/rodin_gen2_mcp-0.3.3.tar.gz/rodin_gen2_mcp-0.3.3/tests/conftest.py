"""Общие fixtures для тестов"""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Мокирует переменные окружения"""
    monkeypatch.setenv("RODIN_API_KEY", "test_api_key_12345")
    monkeypatch.setenv("RODIN_API_BASE_URL", "https://api.test.rodin.com")


@pytest.fixture
def temp_image_file(tmp_path):
    """Создает временный файл изображения для тестов"""
    image_file = tmp_path / "test_image.png"
    # Создаем простой PNG файл (минимальный валидный PNG)
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01'
        b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    image_file.write_bytes(png_data)
    return str(image_file)


@pytest.fixture
def mock_httpx_response():
    """Создает мок-объект для httpx response"""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"result": "success"}
    mock.text = "OK"
    mock.raise_for_status = MagicMock()
    mock.content = b"test content"
    return mock


@pytest.fixture
def mock_async_client(mock_httpx_response):
    """Создает мок AsyncClient для httpx"""
    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_httpx_response)
    mock_client.get = AsyncMock(return_value=mock_httpx_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client

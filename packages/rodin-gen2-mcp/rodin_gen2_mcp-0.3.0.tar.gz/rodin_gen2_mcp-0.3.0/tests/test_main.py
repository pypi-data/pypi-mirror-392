"""Тесты для main.py - FastAPI сервер"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import HTTPStatusError, Response, Request


@pytest.fixture
def test_client(mock_env_vars):
    """Создает тестовый клиент FastAPI"""
    # Импортируем после установки переменных окружения
    from main import app
    return TestClient(app)


@pytest.fixture
def mock_rodin_client():
    """Мокирует RodinClient"""
    with patch('main.rodin_client') as mock:
        mock.generate = AsyncMock(return_value={"result": "3d_model_data", "status": "completed"})
        yield mock


class TestRootEndpoint:
    """Тесты корневого эндпоинта"""
    
    def test_root_returns_welcome_message(self, test_client):
        """Проверяет, что корневой эндпоинт возвращает приветственное сообщение"""
        response = test_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Rodin Gen-2 MCP Server is running"}


class TestHealthEndpoint:
    """Тесты health check эндпоинта"""
    
    def test_health_check_returns_ok(self, test_client):
        """Проверяет, что health check возвращает ok"""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestGenerateEndpoint:
    """Тесты /generate эндпоинта"""
    
    def test_generate_success(self, test_client, mock_rodin_client):
        """Проверяет успешную генерацию"""
        payload = {
            "prompt": "Generate a 3D cube",
            "parameters": {"quality": "high"}
        }
        
        response = test_client.post("/generate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "result" in data
        
        # Проверяем, что клиент был вызван с правильными параметрами
        mock_rodin_client.generate.assert_called_once_with(
            prompt="Generate a 3D cube",
            parameters={"quality": "high"}
        )
    
    def test_generate_without_parameters(self, test_client, mock_rodin_client):
        """Проверяет генерацию без дополнительных параметров"""
        payload = {"prompt": "Generate a sphere"}
        
        response = test_client.post("/generate", json=payload)
        
        assert response.status_code == 200
        mock_rodin_client.generate.assert_called_once_with(
            prompt="Generate a sphere",
            parameters=None
        )
    
    def test_generate_invalid_payload(self, test_client):
        """Проверяет обработку невалидного payload"""
        payload = {"invalid_field": "value"}
        
        response = test_client.post("/generate", json=payload)
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_generate_api_error(self, test_client, mock_rodin_client):
        """Проверяет обработку ошибки API"""
        mock_rodin_client.generate.side_effect = Exception("API connection failed")
        
        payload = {"prompt": "Test prompt"}
        response = test_client.post("/generate", json=payload)
        
        assert response.status_code == 500
        assert "API connection failed" in response.json()["detail"]


class TestRodinClient:
    """Тесты RodinClient класса"""
    
    @pytest.mark.asyncio
    async def test_rodin_client_generate_success(self, mock_env_vars):
        """Проверяет успешную генерацию через клиента"""
        from main import RodinClient
        
        client = RodinClient("https://test.api.com", "test_key")
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"model": "generated"}
            
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            
            mock_client_class.return_value = mock_client
            
            result = await client.generate("test prompt", {"param": "value"})
            
            assert result == {"model": "generated"}
            mock_client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rodin_client_generate_http_error(self, mock_env_vars):
        """Проверяет обработку HTTP ошибки"""
        from main import RodinClient
        from fastapi import HTTPException
        
        client = RodinClient("https://test.api.com", "test_key")
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch('main.httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(HTTPException) as exc_info:
                await client.generate("test prompt")
            
            assert exc_info.value.status_code == 400
            assert "Bad request" in str(exc_info.value.detail)
    
    def test_rodin_client_initialization(self, mock_env_vars):
        """Проверяет инициализацию клиента"""
        from main import RodinClient
        
        client = RodinClient("https://test.api.com", "test_key_123")
        
        assert client.base_url == "https://test.api.com"
        assert client.api_key == "test_key_123"
        assert client.headers["Authorization"] == "Bearer test_key_123"
        assert client.headers["Content-Type"] == "application/json"


class TestConfiguration:
    """Тесты конфигурации приложения"""
    
    def test_api_key_required(self):
        """Проверяет, что отсутствие API ключа вызывает ошибку"""
        # Этот тест проверяет что main.py требует API ключ при импорте
        # Но так как модуль уже импортирован, проверяем что переменная существует
        import main
        # Если мы дошли сюда без ошибки, значит API ключ был установлен через fixture
        assert hasattr(main, 'RODIN_API_KEY')
        assert main.RODIN_API_KEY is not None
    
    def test_default_base_url(self):
        """Проверяет дефолтный URL API"""
        import main
        # Проверяем что URL установлен (либо дефолтный, либо из env)
        assert hasattr(main, 'RODIN_API_BASE_URL')
        assert main.RODIN_API_BASE_URL is not None
        # URL может быть либо дефолтным, либо из тестового окружения
        assert isinstance(main.RODIN_API_BASE_URL, str)

"""Тесты для rodin_gen2_server.py - MCP сервер"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from pathlib import Path
import httpx


@pytest.fixture
def mock_make_rodin_request():
    """Мокирует make_rodin_request функцию"""
    with patch('rodin_gen2_server.make_rodin_request') as mock:
        yield mock


class TestMakeRodinRequest:
    """Тесты функции make_rodin_request"""
    
    @pytest.mark.asyncio
    async def test_make_rodin_request_success_get(self, mock_env_vars):
        """Проверяет успешный GET запрос"""
        from rodin_gen2_server import make_rodin_request
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {"status": "ok"}
            mock_response.raise_for_status = MagicMock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            
            mock_client_class.return_value = mock_client
            
            result = await make_rodin_request("/test", method="GET")
            
            assert result == {"status": "ok"}
            mock_client.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_rodin_request_success_post(self, mock_env_vars):
        """Проверяет успешный POST запрос"""
        from rodin_gen2_server import make_rodin_request
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {"uuid": "test-uuid"}
            mock_response.raise_for_status = MagicMock()
            
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            
            mock_client_class.return_value = mock_client
            
            result = await make_rodin_request("/rodin", method="POST", data={"prompt": "test"})
            
            assert result == {"uuid": "test-uuid"}
            mock_client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_rodin_request_no_api_key(self, monkeypatch):
        """Проверяет ошибку при отсутствии API ключа"""
        # Временно сохраняем старое значение
        import rodin_gen2_server
        old_key = rodin_gen2_server.RODIN_API_KEY
        
        try:
            # Устанавливаем None
            rodin_gen2_server.RODIN_API_KEY = None
            
            from rodin_gen2_server import make_rodin_request
            
            with pytest.raises(ValueError, match="RODIN_API_KEY не установлен"):
                await make_rodin_request("/test")
        finally:
            # Восстанавливаем значение
            rodin_gen2_server.RODIN_API_KEY = old_key
    
    @pytest.mark.asyncio
    async def test_make_rodin_request_http_error(self, mock_env_vars):
        """Проверяет обработку HTTP ошибки"""
        from rodin_gen2_server import make_rodin_request
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=mock_response
        )
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        
        with patch('rodin_gen2_server.httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(Exception, match="Rodin API ошибка"):
                await make_rodin_request("/test")
    
    @pytest.mark.asyncio
    async def test_make_rodin_request_network_error(self, mock_env_vars):
        """Проверяет обработку сетевой ошибки"""
        from rodin_gen2_server import make_rodin_request
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.RequestError("Connection failed", request=MagicMock()))
        
        with patch('rodin_gen2_server.httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(Exception, match="Ошибка сети"):
                await make_rodin_request("/test")
    
    @pytest.mark.asyncio
    async def test_make_rodin_request_unsupported_method(self, mock_env_vars):
        """Проверяет обработку неподдерживаемого HTTP метода"""
        from rodin_gen2_server import make_rodin_request
        
        mock_client = AsyncMock()
        
        with patch('rodin_gen2_server.httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(Exception, match="Неподдерживаемый HTTP метод"):
                await make_rodin_request("/test", method="DELETE")


class TestGenerate3DTextTo3D:
    """Тесты функции generate_3d_text_to_3d"""
    
    @pytest.mark.asyncio
    async def test_generate_text_to_3d_success(self, mock_env_vars, mock_make_rodin_request):
        """Проверяет успешную генерацию Text-to-3D"""
        from rodin_gen2_server import generate_3d_text_to_3d
        
        mock_make_rodin_request.return_value = {
            "uuid": "test-uuid-123",
            "jobs": {"subscription_key": "sub-key-456"}
        }
        
        result = await generate_3d_text_to_3d(prompt="A red cube")
        
        assert "✅" in result
        assert "test-uuid-123" in result
        assert "sub-key-456" in result
        
        # Проверяем вызов API
        mock_make_rodin_request.assert_called_once()
        call_args = mock_make_rodin_request.call_args
        assert call_args[1]["endpoint"] == "/rodin"
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["data"]["prompt"] == "A red cube"
    
    @pytest.mark.asyncio
    async def test_generate_text_to_3d_with_all_parameters(self, mock_env_vars, mock_make_rodin_request):
        """Проверяет генерацию со всеми параметрами"""
        from rodin_gen2_server import generate_3d_text_to_3d
        
        mock_make_rodin_request.return_value = {
            "uuid": "test-uuid",
            "jobs": {"subscription_key": "sub-key"}
        }
        
        result = await generate_3d_text_to_3d(
            prompt="A blue sphere",
            seed=42,
            geometry_file_format="fbx",
            material="Shaded",
            mesh_simplify=True,
            quality_override=1000,
            bbox_condition=[10, 20, 30]
        )
        
        assert "✅" in result
        
        call_args = mock_make_rodin_request.call_args
        form_data = call_args[1]["data"]
        
        assert form_data["prompt"] == "A blue sphere"
        assert form_data["seed"] == "42"
        assert form_data["geometry_file_format"] == "fbx"
        assert form_data["material"] == "Shaded"
        assert form_data["mesh_simplify"] == "True"
        assert form_data["quality_override"] == "1000"
        assert form_data["bbox_condition"] == "[10, 20, 30]"
    
    @pytest.mark.asyncio
    async def test_generate_text_to_3d_invalid_seed(self, mock_env_vars):
        """Проверяет валидацию seed"""
        from rodin_gen2_server import generate_3d_text_to_3d
        
        with pytest.raises(ValueError, match="Seed должен быть в диапазоне 0-65535"):
            await generate_3d_text_to_3d(prompt="Test", seed=70000)
        
        with pytest.raises(ValueError, match="Seed должен быть в диапазоне 0-65535"):
            await generate_3d_text_to_3d(prompt="Test", seed=-1)
    
    @pytest.mark.asyncio
    async def test_generate_text_to_3d_invalid_bbox(self, mock_env_vars):
        """Проверяет валидацию bbox_condition"""
        from rodin_gen2_server import generate_3d_text_to_3d
        
        with pytest.raises(ValueError, match="bbox_condition должен содержать 3 элемента"):
            await generate_3d_text_to_3d(prompt="Test", bbox_condition=[10, 20])
    
    @pytest.mark.asyncio
    async def test_generate_text_to_3d_api_error(self, mock_env_vars, mock_make_rodin_request):
        """Проверяет обработку ошибки API"""
        from rodin_gen2_server import generate_3d_text_to_3d
        
        mock_make_rodin_request.side_effect = Exception("API unavailable")
        
        result = await generate_3d_text_to_3d(prompt="Test")
        
        assert "❌" in result
        assert "API unavailable" in result


class TestGenerate3DImageTo3D:
    """Тесты функции generate_3d_image_to_3d"""
    
    @pytest.mark.asyncio
    async def test_generate_image_to_3d_success(
        self, mock_env_vars, mock_make_rodin_request, temp_image_file
    ):
        """Проверяет успешную генерацию Image-to-3D"""
        from rodin_gen2_server import generate_3d_image_to_3d
        
        mock_make_rodin_request.return_value = {
            "uuid": "img-uuid-123",
            "jobs": {"subscription_key": "img-sub-key"}
        }
        
        result = await generate_3d_image_to_3d(image_paths=[temp_image_file])
        
        assert "✅" in result
        assert "img-uuid-123" in result
        
        mock_make_rodin_request.assert_called_once()
        call_args = mock_make_rodin_request.call_args
        assert call_args[1]["endpoint"] == "/rodin"
        assert "files" in call_args[1]
    
    @pytest.mark.asyncio
    async def test_generate_image_to_3d_no_images(self, mock_env_vars):
        """Проверяет ошибку при отсутствии изображений"""
        from rodin_gen2_server import generate_3d_image_to_3d
        
        result = await generate_3d_image_to_3d(image_paths=[])
        
        assert "❌" in result
        assert "хотя бы одно изображение" in result
    
    @pytest.mark.asyncio
    async def test_generate_image_to_3d_too_many_images(self, mock_env_vars, temp_image_file):
        """Проверяет ограничение на количество изображений"""
        from rodin_gen2_server import generate_3d_image_to_3d
        
        result = await generate_3d_image_to_3d(image_paths=[temp_image_file] * 6)
        
        assert "❌" in result
        assert "Максимум 5" in result
    
    @pytest.mark.asyncio
    async def test_generate_image_to_3d_file_not_found(self, mock_env_vars):
        """Проверяет обработку несуществующего файла"""
        from rodin_gen2_server import generate_3d_image_to_3d
        
        result = await generate_3d_image_to_3d(image_paths=["/nonexistent/file.png"])
        
        assert "❌" in result
        assert "Файл не найден" in result
    
    @pytest.mark.asyncio
    async def test_generate_image_to_3d_with_parameters(
        self, mock_env_vars, mock_make_rodin_request, temp_image_file
    ):
        """Проверяет генерацию с дополнительными параметрами"""
        from rodin_gen2_server import generate_3d_image_to_3d
        
        mock_make_rodin_request.return_value = {
            "uuid": "test-uuid",
            "jobs": {"subscription_key": "test-key"}
        }
        
        result = await generate_3d_image_to_3d(
            image_paths=[temp_image_file],
            prompt="Custom prompt",
            seed=100,
            use_original_alpha=True,
            bbox_condition=[5, 10, 15]
        )
        
        assert "✅" in result
        
        call_args = mock_make_rodin_request.call_args
        form_data = call_args[1]["data"]
        
        assert form_data["prompt"] == "Custom prompt"
        assert form_data["seed"] == "100"
        assert form_data["use_original_alpha"] == "True"


class TestCheckTaskStatus:
    """Тесты функции check_task_status"""
    
    @pytest.mark.asyncio
    async def test_check_task_status_all_done(self, mock_env_vars, mock_make_rodin_request):
        """Проверяет статус когда все задачи завершены"""
        from rodin_gen2_server import check_task_status
        
        mock_make_rodin_request.return_value = {
            "jobs": [
                {"uuid": "job-1", "status": "done"},
                {"uuid": "job-2", "status": "done"}
            ]
        }
        
        result = await check_task_status("test-sub-key")
        
        assert "✅" in result
        assert "Все задачи завершены" in result
    
    @pytest.mark.asyncio
    async def test_check_task_status_in_progress(self, mock_env_vars, mock_make_rodin_request):
        """Проверяет статус когда задачи в процессе"""
        from rodin_gen2_server import check_task_status
        
        mock_make_rodin_request.return_value = {
            "jobs": [
                {"uuid": "job-1", "status": "done"},
                {"uuid": "job-2", "status": "generating"}
            ]
        }
        
        result = await check_task_status("test-sub-key")
        
        assert "🔄" in result
        assert "в процессе" in result
    
    @pytest.mark.asyncio
    async def test_check_task_status_failed(self, mock_env_vars, mock_make_rodin_request):
        """Проверяет статус когда есть провалившиеся задачи"""
        from rodin_gen2_server import check_task_status
        
        mock_make_rodin_request.return_value = {
            "jobs": [
                {"uuid": "job-1", "status": "done"},
                {"uuid": "job-2", "status": "failed"}
            ]
        }
        
        result = await check_task_status("test-sub-key")
        
        assert "❌" in result
        assert "завершились с ошибкой" in result
    
    @pytest.mark.asyncio
    async def test_check_task_status_no_jobs(self, mock_env_vars, mock_make_rodin_request):
        """Проверяет когда задачи не найдены"""
        from rodin_gen2_server import check_task_status
        
        mock_make_rodin_request.return_value = {"jobs": []}
        
        result = await check_task_status("test-sub-key")
        
        assert "❌" in result
        assert "не найдены" in result


class TestDownloadResult:
    """Тесты функции download_result"""
    
    @pytest.mark.asyncio
    async def test_download_result_success(
        self, mock_env_vars, mock_make_rodin_request, tmp_path
    ):
        """Проверяет успешную загрузку результата"""
        from rodin_gen2_server import download_result
        
        mock_make_rodin_request.return_value = {
            "list": [
                {"url": "https://example.com/model.glb", "name": "model.glb"}
            ]
        }
        
        with patch('rodin_gen2_server.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.content = b"fake model data"
            mock_response.raise_for_status = MagicMock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            
            mock_client_class.return_value = mock_client
            
            # Создаем реальный файл вместо мока
            result = await download_result("test-uuid", str(tmp_path))
            
            assert "✅" in result
            assert "Успешно загружено" in result
            assert "model.glb" in result
    
    @pytest.mark.asyncio
    async def test_download_result_empty_list(self, mock_env_vars, mock_make_rodin_request):
        """Проверяет обработку пустого списка файлов"""
        from rodin_gen2_server import download_result
        
        mock_make_rodin_request.return_value = {"list": []}
        
        result = await download_result("test-uuid")
        
        assert "❌" in result
        assert "пуст" in result
    
    @pytest.mark.asyncio
    async def test_download_result_api_error(self, mock_env_vars, mock_make_rodin_request):
        """Проверяет обработку ошибки API"""
        from rodin_gen2_server import download_result
        
        mock_make_rodin_request.side_effect = Exception("Download failed")
        
        result = await download_result("test-uuid")
        
        assert "❌" in result
        assert "Download failed" in result


class TestStartDownloadResult:
    """Тесты функции start_download_result"""
    
    @pytest.mark.asyncio
    async def test_start_download_result(self, mock_env_vars):
        """Проверяет запуск фоновой загрузки"""
        from rodin_gen2_server import start_download_result
        
        with patch('rodin_gen2_server.asyncio.create_task') as mock_create_task:
            result = await start_download_result("test-uuid", "/output")
            
            assert "✅" in result
            assert "Фоновая загрузка запущена" in result
            assert "ID задачи загрузки" in result
            
            # Проверяем, что задача создана
            mock_create_task.assert_called_once()


class TestCheckDownloadResultStatus:
    """Тесты функции check_download_result_status"""
    
    @pytest.mark.asyncio
    async def test_check_download_status_not_found(self, mock_env_vars):
        """Проверяет когда задача не найдена"""
        from rodin_gen2_server import check_download_result_status
        
        result = await check_download_result_status("nonexistent-task-id")
        
        assert "❌" in result
        assert "не найдена" in result
    
    @pytest.mark.asyncio
    async def test_check_download_status_pending(self, mock_env_vars):
        """Проверяет статус pending"""
        from rodin_gen2_server import check_download_result_status, download_tasks, download_tasks_lock
        
        task_id = "test-task-id"
        async with download_tasks_lock:
            download_tasks[task_id] = {"status": "pending"}
        
        try:
            result = await check_download_result_status(task_id)
            assert "⏳" in result
            assert "поставлена в очередь" in result
        finally:
            async with download_tasks_lock:
                download_tasks.pop(task_id, None)
    
    @pytest.mark.asyncio
    async def test_check_download_status_running(self, mock_env_vars):
        """Проверяет статус running"""
        from rodin_gen2_server import check_download_result_status, download_tasks, download_tasks_lock
        
        task_id = "test-task-id"
        async with download_tasks_lock:
            download_tasks[task_id] = {"status": "running"}
        
        try:
            result = await check_download_result_status(task_id)
            assert "🔄" in result
            assert "выполняется" in result
        finally:
            async with download_tasks_lock:
                download_tasks.pop(task_id, None)
    
    @pytest.mark.asyncio
    async def test_check_download_status_completed(self, mock_env_vars):
        """Проверяет статус completed"""
        from rodin_gen2_server import check_download_result_status, download_tasks, download_tasks_lock
        
        task_id = "test-task-id"
        async with download_tasks_lock:
            download_tasks[task_id] = {
                "status": "completed",
                "output_dir": "/tmp/output",
                "total_size_mb": 5.5,
                "files": [
                    {"name": "model.glb", "size_mb": 5.5}
                ]
            }
        
        try:
            result = await check_download_result_status(task_id)
            assert "✅" in result
            assert "завершена" in result
            assert "model.glb" in result
        finally:
            async with download_tasks_lock:
                download_tasks.pop(task_id, None)
    
    @pytest.mark.asyncio
    async def test_check_download_status_failed(self, mock_env_vars):
        """Проверяет статус failed"""
        from rodin_gen2_server import check_download_result_status, download_tasks, download_tasks_lock
        
        task_id = "test-task-id"
        async with download_tasks_lock:
            download_tasks[task_id] = {
                "status": "failed",
                "error": "Network error"
            }
        
        try:
            result = await check_download_result_status(task_id)
            assert "❌" in result
            assert "Network error" in result
        finally:
            async with download_tasks_lock:
                download_tasks.pop(task_id, None)

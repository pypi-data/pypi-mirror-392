#!/usr/bin/env python3
"""
MCP Server для Rodin Gen-2 API
Предоставляет инструменты для генерации 3D моделей через Rodin Gen-2 API
"""

import os
import logging
import asyncio
import uuid
import argparse
import time
from typing import Any, Optional
from pathlib import Path

import httpx
import aiofiles
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования (используем stderr, не stdout для STDIO транспорта)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def setup_logging(log_file: Optional[str] = None) -> None:
    """
    Настраивает логирование в файл для диагностики проблем.
    
    Args:
        log_file: Путь к файлу для записи логов. Если None, логирование только в stderr.
    """
    if log_file:
        # Создаем file handler для записи в файл
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Детальное логирование в файл
        
        # Форматтер для файла - более подробный
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Добавляем handler к root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.DEBUG)  # Устанавливаем DEBUG уровень для root logger
        
        logger.info(f"Логирование в файл настроено: {log_file}")
        logger.debug("Режим детального логирования активирован")

download_tasks: dict[str, dict[str, Any]] = {}
download_tasks_lock: Optional[asyncio.Lock] = None
download_semaphore: Optional[asyncio.Semaphore] = None


def get_download_lock() -> asyncio.Lock:
    """Получает или создаёт Lock для текущего event loop"""
    global download_tasks_lock
    if download_tasks_lock is None:
        download_tasks_lock = asyncio.Lock()
    return download_tasks_lock


def get_download_semaphore() -> asyncio.Semaphore:
    """Получает или создаёт Semaphore для текущего event loop"""
    global download_semaphore
    if download_semaphore is None:
        download_semaphore = asyncio.Semaphore(1)  # Максимум 1 одновременная загрузка
    return download_semaphore


# Инициализация FastMCP сервера
mcp = FastMCP("rodin-gen2")

# Константы
RODIN_API_BASE_URL = "https://api.hyper3d.com/api/v2"
RODIN_API_KEY = os.getenv("RODIN_API_KEY")

if not RODIN_API_KEY:
    logger.warning("RODIN_API_KEY не установлен в переменных окружения")


async def make_rodin_request(
    endpoint: str,
    method: str = "GET",
    files: Optional[dict] = None,
    data: Optional[dict] = None,
    timeout: float = 60.0
) -> dict[str, Any]:
    """
    Выполняет запрос к Rodin API с обработкой ошибок
    
    Args:
        endpoint: Конечная точка API (например, "/rodin")
        method: HTTP метод (GET, POST и т.д.)
        files: Файлы для multipart/form-data запроса
        data: Данные формы
        timeout: Таймаут запроса в секундах
        
    Returns:
        Ответ API в формате JSON
        
    Raises:
        Exception: При ошибках API или сети
    """
    if not RODIN_API_KEY:
        raise ValueError("RODIN_API_KEY не установлен. Установите его в .env файле")
    
    headers = {
        "Authorization": f"Bearer {RODIN_API_KEY}"
    }
    
    url = f"{RODIN_API_BASE_URL}{endpoint}"
    
    logger.debug(f"Начало запроса: {method} {url} (timeout={timeout}s)")
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            if method.upper() == "POST" and files:
                # Для multipart/form-data запросов
                logger.debug(f"POST запрос с файлами: {len(files)} файл(ов)")
                response = await client.post(url, headers=headers, files=files, data=data)
            elif method.upper() == "POST":
                logger.debug(f"POST запрос с данными: {data}")
                response = await client.post(url, headers=headers, data=data)
            elif method.upper() == "GET":
                logger.debug("GET запрос")
                response = await client.get(url, headers=headers)
            else:
                raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
            
            elapsed_time = time.time() - start_time
            logger.debug(f"Ответ получен за {elapsed_time:.2f}s, status={response.status_code}")
            
            response.raise_for_status()
            response_json = response.json()
            
            logger.debug(f"JSON ответ размером ~{len(str(response_json))} символов")
            return response_json
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(f"HTTP ошибка {e.response.status_code}: {error_detail}")
            raise Exception(f"Rodin API ошибка ({e.response.status_code}): {error_detail}")
        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса: {str(e)}")
            raise Exception(f"Ошибка сети при обращении к Rodin API: {str(e)}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {str(e)}")
            raise


@mcp.tool()
async def generate_3d_text_to_3d(
    prompt: str,
    seed: Optional[int] = None,
    geometry_file_format: str = "glb",
    material: str = "PBR",
    mesh_simplify: bool = False,
    quality_override: Optional[int] = None,
    bbox_condition: Optional[list[int]] = None
) -> str:
    """
    Генерирует 3D модель из текстового описания (Text-to-3D)
    
    Args:
        prompt: Текстовое описание 3D модели для генерации
        seed: Seed для воспроизводимости (0-65535). Опционально
        geometry_file_format: Формат файла (glb, usdz, fbx, obj, stl). По умолчанию glb
        material: Тип материала (PBR, Shaded, All). По умолчанию PBR
        mesh_simplify: Упростить меш. По умолчанию False
        quality_override: Переопределение качества (количество полигонов). Опционально
        bbox_condition: Условие bounding box [width, height, length]. Опционально
        
    Returns:
        UUID задачи для проверки статуса и загрузки результата
    """
    # Подготовка данных формы
    form_data = {
        "tier": "Gen-2",
        "prompt": prompt,
        "geometry_file_format": geometry_file_format,
        "material": material,
        "mesh_simplify": str(mesh_simplify)
    }
    
    if seed is not None:
        if not (0 <= seed <= 65535):
            raise ValueError("Seed должен быть в диапазоне 0-65535")
        form_data["seed"] = str(seed)
    
    if quality_override is not None:
        form_data["quality_override"] = str(quality_override)
    
    if bbox_condition:
        if len(bbox_condition) != 3:
            raise ValueError("bbox_condition должен содержать 3 элемента [width, height, length]")
        form_data["bbox_condition"] = str(bbox_condition)
    
    try:
        logger.debug(f"Генерация Text-to-3D с параметрами: prompt='{prompt[:50]}...', seed={seed}, format={geometry_file_format}")
        result = await make_rodin_request(
            endpoint="/rodin",
            method="POST",
            data=form_data,
            timeout=120.0
        )
        
        logger.debug("Получен ответ от API для Text-to-3D генерации")
        uuid = result.get("uuid")
        jobs = result.get("jobs", {})
        subscription_key = jobs.get("subscription_key")
        
        if not uuid:
            raise Exception("API не вернул UUID задачи")
        
        logger.info(f"Задача создана успешно. UUID: {uuid}")
        
        message = f"✅ Задача генерации создана успешно!\n\n"
        message += f"📋 UUID задачи: {uuid}\n"
        
        if subscription_key:
            message += f"🔑 Subscription Key: {subscription_key}\n\n"
            message += "Рекомендуемый сценарий:\n"
            message += f"  1) Проверяйте прогресс через tool check_task_status с subscription_key '{subscription_key}'.\n"
            message += f"  2) Когда все подзадачи в статусе done, вызовите start_download_result с UUID '{uuid}' (и при необходимости output_dir).\n"
            message += "  3) Отслеживайте ход загрузки через check_download_result_status по ID задачи загрузки.\n\n"
            message += "Альтернатива: можно использовать download_result с UUID задачи, но этот инструмент выполняет загрузку синхронно и может занимать больше времени."
        else:
            message += f"\n⚠️ Внимание: subscription_key не найден в ответе API. Вы сможете сразу вызвать start_download_result с UUID задачи для загрузки результата."
        
        return message
        
    except Exception as e:
        logger.error(f"Ошибка при генерации: {str(e)}")
        return f"❌ Ошибка при создании задачи генерации: {str(e)}"


@mcp.tool()
async def generate_3d_image_to_3d(
    image_paths: list[str],
    prompt: Optional[str] = None,
    use_original_alpha: bool = False,
    seed: Optional[int] = None,
    geometry_file_format: str = "glb",
    material: str = "PBR",
    mesh_simplify: bool = False,
    quality_override: Optional[int] = None,
    condition_mode: str = "concat",
    bbox_condition: Optional[list[int]] = None
) -> str:
    """
    Генерирует 3D модель из изображения(й) (Image-to-3D)
    
    Args:
        image_paths: Список путей к изображениям (до 5 файлов)
        prompt: Текстовое описание. Опционально (если не указано, будет сгенерировано AI)
        use_original_alpha: Использовать оригинальный альфа-канал. По умолчанию False
        seed: Seed для воспроизводимости (0-65535). Опционально
        geometry_file_format: Формат файла (glb, usdz, fbx, obj, stl). По умолчанию glb
        material: Тип материала (PBR, Shaded, All). По умолчанию PBR
        mesh_simplify: Упростить меш. По умолчанию False
        quality_override: Переопределение качества. Опционально
        condition_mode: Режим для множественных изображений (concat). По умолчанию concat
        bbox_condition: Условие bounding box [width, height, length]. Опционально
        
    Returns:
        UUID задачи для проверки статуса и загрузки результата
    """
    if not image_paths:
        return "❌ Необходимо указать хотя бы одно изображение"
    
    if len(image_paths) > 5:
        return "❌ Максимум 5 изображений разрешено"
    
    # Подготовка файлов
    files = []
    data = {
        "tier": "Gen-2",
        "geometry_file_format": geometry_file_format,
        "material": material,
        "mesh_simplify": str(mesh_simplify),
        "use_original_alpha": str(use_original_alpha)
    }
    
    # Открываем и читаем файлы изображений
    try:
        logger.debug(f"Генерация Image-to-3D из {len(image_paths)} изображений, seed={seed}, format={geometry_file_format}")
        for image_path in image_paths:
            path = Path(image_path)
            if not path.exists():
                return f"❌ Файл не найден: {image_path}"
            
            with open(path, 'rb') as f:
                image_data = f.read()
                # Определяем MIME тип на основе расширения
                ext = path.suffix.lower()
                mime_type = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.webp': 'image/webp'
                }.get(ext, 'image/jpeg')
                
                files.append(('images', (path.name, image_data, mime_type)))
        
        if prompt:
            data["prompt"] = prompt
        
        if seed is not None:
            if not (0 <= seed <= 65535):
                return "❌ Seed должен быть в диапазоне 0-65535"
            data["seed"] = str(seed)
        
        if quality_override is not None:
            data["quality_override"] = str(quality_override)
        
        if len(image_paths) > 1:
            data["condition_mode"] = condition_mode
        
        if bbox_condition:
            if len(bbox_condition) != 3:
                return "❌ bbox_condition должен содержать 3 элемента [width, height, length]"
            data["bbox_condition"] = str(bbox_condition)
        
        result = await make_rodin_request(
            endpoint="/rodin",
            method="POST",
            files=files,
            data=data,
            timeout=120.0
        )
        
        uuid = result.get("uuid")
        jobs = result.get("jobs", {})
        subscription_key = jobs.get("subscription_key")
        
        if not uuid:
            raise Exception("API не вернул UUID задачи")
        
        logger.info(f"Задача создана успешно. UUID: {uuid}")
        
        message = f"✅ Задача генерации создана успешно!\n\n"
        message += f"📋 UUID задачи: {uuid}\n"
        
        if subscription_key:
            message += f"🔑 Subscription Key: {subscription_key}\n\n"
            message += "Рекомендуемый сценарий:\n"
            message += f"  1) Проверяйте прогресс через tool check_task_status с subscription_key '{subscription_key}'.\n"
            message += f"  2) Когда все подзадачи в статусе done, вызовите start_download_result с UUID '{uuid}' (и при необходимости output_dir).\n"
            message += "  3) Отслеживайте ход загрузки через check_download_result_status по ID задачи загрузки.\n\n"
            message += "Альтернатива: можно использовать download_result с UUID задачи, но этот инструмент выполняет загрузку синхронно и может занимать больше времени."
        else:
            message += f"\n⚠️ Внимание: subscription_key не найден в ответе API. Вы сможете сразу вызвать start_download_result с UUID задачи для загрузки результата."
        
        return message
        
    except Exception as e:
        logger.error(f"Ошибка при генерации: {str(e)}")
        return f"❌ Ошибка при создании задачи генерации: {str(e)}"


@mcp.tool()
async def check_task_status(subscription_key: str) -> str:
    """
    Проверяет статус задачи генерации
    
    Args:
        subscription_key: Subscription key задачи (jobs.subscription_key из ответа generate_3d_*)
        
    Returns:
        Текущий статус всех подзадач
    """
    try:
        logger.debug(f"Проверка статуса задачи с subscription_key: {subscription_key[:16]}...")
        result = await make_rodin_request(
            endpoint="/status",
            method="POST",
            data={"subscription_key": subscription_key},
            timeout=5.0
        )
        
        logger.debug(f"Получен ответ для проверки статуса: {len(result.get('jobs', []))} задач(и)")
        
        # Даём контроль event loop после HTTP запроса
        await asyncio.sleep(0)
        
        jobs = result.get("jobs", [])
        
        if not jobs:
            return "❌ Задачи не найдены"
        
        message = "📊 Статус задач:\n\n"
        
        for job in jobs:
            uuid = job.get("uuid", "unknown")
            status = job.get("status", "unknown")
            
            status_emoji = {
                "waiting": "⏳",
                "generating": "🔄",
                "done": "✅",
                "failed": "❌"
            }.get(status.lower(), "❓")
            
            message += f"{status_emoji} UUID: {uuid}\n"
            message += f"   Статус: {status}\n\n"
            
            # Даём контроль event loop после каждой задачи
            await asyncio.sleep(0)
        
        # Проверяем, все ли задачи завершены
        all_done = all(job.get("status", "").lower() == "done" for job in jobs)
        any_failed = any(job.get("status", "").lower() == "failed" for job in jobs)
        
        if all_done:
            message += "✅ Все задачи завершены! Используйте download_result для загрузки файлов."
        elif any_failed:
            message += "❌ Некоторые задачи завершились с ошибкой."
        else:
            message += "🔄 Генерация в процессе. Проверьте статус позже."
        
        return message
        
    except Exception as e:
        logger.error(f"❌ Ошибка проверки статуса: {str(e)[:100]}")
        return f"❌ Ошибка при проверке статуса: {str(e)}"


async def _download_result_background(task_uuid: str, output_dir: Optional[str], task_id: str) -> None:
    # Ограничиваем количество одновременных загрузок через семафор
    logger.debug(f"Начало фоновой загрузки: task_uuid={task_uuid}, task_id={task_id}")
    async with get_download_semaphore():
        logger.debug(f"Получен слот семафора для загрузки {task_id}")
        try:
            async with get_download_lock():
                task_info = download_tasks.get(task_id)
                if task_info is not None:
                    task_info["status"] = "running"
            
            logger.debug(f"Запрашиваем список файлов для task_uuid={task_uuid}")
            result = await make_rodin_request(
                endpoint="/download",
                method="POST",
                data={"task_uuid": task_uuid},
                timeout=5.0
            )

            file_list = result.get("list", [])

            if not file_list:
                raise Exception("Список файлов пуст. Возможно, задача еще не завершена.")

            logger.info(f"Получен список из {len(file_list)} файл(ов) для загрузки")
            # Даём контроль event loop после логирования
            await asyncio.sleep(0)

            if output_dir is None:
                output_dir = "."

            output_directory = Path(output_dir)
            # Используем asyncio.to_thread для синхронной операции mkdir
            await asyncio.to_thread(output_directory.mkdir, parents=True, exist_ok=True)

            downloaded_files: list[dict[str, Any]] = []
            total_size = 0
            failed_files: list[str] = []

            # Создаем отдельный HTTP клиент для этой задачи
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(120.0, read=300.0),  # Увеличенный timeout для больших файлов
                limits=httpx.Limits(max_connections=5, max_keepalive_connections=2)
            ) as client:
                for idx, file_info in enumerate(file_list, 1):
                    file_url = file_info.get("url")
                    file_name = file_info.get("name", "unnamed_file")

                    if not file_url:
                        logger.warning(f"[{idx}/{len(file_list)}] Пропущен файл без URL: {file_name}")
                        failed_files.append(f"{file_name} (нет URL)")
                        continue

                    output_file = output_directory / file_name

                    try:
                        # Потоковая загрузка вместо загрузки всего файла в память
                        async with client.stream('GET', file_url) as response:
                            response.raise_for_status()
                            async with aiofiles.open(output_file, 'wb') as f:
                                chunk_count = 0
                                async for chunk in response.aiter_bytes(chunk_size=65536):  # 64KB chunks
                                    await f.write(chunk)
                                    chunk_count += 1
                                    # Даём контроль event loop каждые 100 чанков (~6.4MB)
                                    if chunk_count % 100 == 0:
                                        await asyncio.sleep(0)

                        # Используем asyncio.to_thread для синхронной операции stat()
                        file_size = await asyncio.to_thread(lambda: output_file.stat().st_size)
                        total_size += file_size
                        size_mb = file_size / (1024 * 1024)

                        # Используем asyncio.to_thread для absolute()
                        file_path = await asyncio.to_thread(lambda: str(output_file.absolute()))
                        downloaded_files.append(
                            {
                                "name": file_name,
                                "path": file_path,
                                "size_mb": round(size_mb, 2),
                            }
                        )
                        # Даём контроль event loop после загрузки файла
                        await asyncio.sleep(0)
                    
                    except Exception as file_error:
                        logger.error(f"❌ Ошибка при загрузке {file_name}: {str(file_error)[:100]}")
                        failed_files.append(f"{file_name} ({str(file_error)[:50]})")
                        # Даём контроль event loop после ошибки
                        await asyncio.sleep(0)

            total_size_mb = total_size / (1024 * 1024)
            
            # Используем asyncio.to_thread для absolute()
            output_dir_abs = await asyncio.to_thread(lambda: str(output_directory.absolute()))
            
            logger.info(f"✅ Загрузка завершена: {len(downloaded_files)}/{len(file_list)} файлов, {total_size_mb:.1f}MB")
            await asyncio.sleep(0)
            
            async with get_download_lock():
                task_info = download_tasks.get(task_id)
                if task_info is not None:
                    task_info["status"] = "completed" if not failed_files else "completed_with_errors"
                    task_info["files"] = downloaded_files
                    task_info["failed_files"] = failed_files
                    task_info["output_dir"] = output_dir_abs
                    task_info["total_size_mb"] = round(total_size_mb, 2)

        except Exception as e:
            logger.error(f"Ошибка при фоновой загрузке результата: {str(e)}")
            async with get_download_lock():
                task_info = download_tasks.get(task_id)
                if task_info is not None:
                    task_info["status"] = "failed"
                    task_info["error"] = str(e)


@mcp.tool()
async def start_download_result(task_uuid: str, output_dir: Optional[str] = None) -> str:
    """
    Запускает фоновую загрузку результатов 3D-задачи по её UUID.

    Предназначен для LLM-агентов:
      1. Вызывается после того, как генерация завершена (см. check_task_status).
      2. Не блокирует диалог — только стартует фоновую загрузку.
      3. Возвращает идентификатор task_id, который нужно передать в check_download_result_status.

    Args:
        task_uuid: UUID задачи из generate_3d_* (поле uuid, не subscription_key).
        output_dir: Папка для сохранения файлов; по умолчанию — текущая директория.

    Returns:
        Человекочитаемое сообщение с task_id фоновой задачи загрузки.
    """
    task_id = str(uuid.uuid4())
    logger.info(f"Запуск фоновой загрузки для task_uuid={task_uuid}, download_task_id={task_id}")
    logger.debug(f"Output directory: {output_dir or 'current directory'}")

    async with get_download_lock():
        download_tasks[task_id] = {
            "status": "pending",
            "error": None,
            "files": [],
            "output_dir": output_dir,
            "total_size_mb": 0.0,
            "task_uuid": task_uuid,
        }

    asyncio.create_task(_download_result_background(task_uuid, output_dir, task_id))
    logger.debug(f"Фоновая задача загрузки создана: {task_id}")

    message = "✅ Фоновая загрузка запущена!\n\n"
    message += f"📋 ID задачи загрузки: {task_id}\n"
    message += "Используйте check_download_result_status с этим ID, чтобы проверить статус."
    return message


@mcp.tool()
async def check_download_result_status(task_id: str) -> str:
    """
    Проверяет прогресс фоновой загрузки, запущенной start_download_result.

    Удобен для LLM: его можно вызывать периодически, чтобы отслеживать статус
    фоновой загрузки без долгих блокировок одного запроса.

    Args:
        task_id: Идентификатор задачи загрузки, полученный из start_download_result.

    Returns:
        Человекочитаемое сообщение со статусом задачи и, при завершении, списком файлов.
    """
    async with get_download_lock():
        task_info = download_tasks.get(task_id)

    if not task_info:
        return "❌ Задача загрузки не найдена."

    status = task_info.get("status", "unknown")

    if status == "pending":
        return "⏳ Задача загрузки поставлена в очередь (ожидает слота для загрузки, максимум 1 одновременная)."
    if status == "running":
        return "🔄 Загрузка результата выполняется."
    if status == "failed":
        error = task_info.get("error") or "Неизвестная ошибка"
        return f"❌ Задача загрузки завершилась с ошибкой: {error}"
    if status not in ["completed", "completed_with_errors"]:
        return f"❓ Неизвестный статус задачи: {status}"

    failed_files = task_info.get("failed_files", [])
    
    if status == "completed_with_errors":
        message = "⚠️ Загрузка завершена с ошибками!\n\n"
    else:
        message = "✅ Загрузка результата завершена!\n\n"
    
    output_dir = task_info.get("output_dir")
    total_size_mb = task_info.get("total_size_mb", 0.0)

    if output_dir:
        message += f"📁 Директория: {output_dir}\n"
    message += f"💾 Общий размер: {total_size_mb:.2f} MB\n\n"

    files = task_info.get("files") or []
    if files:
        message += f"✅ Успешно загружено ({len(files)} файл(ов)):\n"
        for file_info in files:
            name = file_info.get("name", "unknown")
            size_mb = file_info.get("size_mb", 0.0)
            message += f"  • {name} ({size_mb} MB)\n"
    
    if failed_files:
        message += f"\n❌ Не удалось загрузить ({len(failed_files)} файл(ов)):\n"
        for failed_file in failed_files:
            message += f"  • {failed_file}\n"

    return message


@mcp.tool()
async def download_result(task_uuid: str, output_dir: Optional[str] = None) -> str:
    """
    Синхронно загружает результаты генерации 3D модели по UUID задачи.

    Этот инструмент блокирующий: LLM дожидается завершения загрузки в рамках одного вызова.
    Обычно предпочтительнее использовать пару start_download_result + check_download_result_status,
    но download_result удобен для простых сценариев и небольших объёмов данных.

    Args:
        task_uuid: UUID задачи из generate_3d_* (поле uuid, не subscription_key).
        output_dir: Папка для сохранения файлов; по умолчанию — текущая директория.

    Returns:
        Человекочитаемое сообщение с директорией, суммарным размером и списком загруженных файлов
        либо сообщение об ошибке.
    """
    try:
        logger.info(f"Синхронная загрузка результатов для task_uuid={task_uuid}")
        logger.debug(f"Output directory: {output_dir or 'current directory'}")
        # Получаем список файлов для загрузки
        result = await make_rodin_request(
            endpoint="/download",
            method="POST",
            data={"task_uuid": task_uuid},
            timeout=5.0
        )
        
        file_list = result.get("list", [])
        
        if not file_list:
            return "❌ Список файлов пуст. Возможно, задача еще не завершена. Проверьте статус с помощью check_task_status."
        
        # Определяем директорию для сохранения
        if output_dir is None:
            output_dir = "."
        
        output_directory = Path(output_dir)
        # Используем asyncio.to_thread для синхронной операции mkdir
        await asyncio.to_thread(output_directory.mkdir, parents=True, exist_ok=True)
        
        downloaded_files = []
        total_size = 0
        
        # Загружаем каждый файл
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, read=300.0)) as client:
            for file_info in file_list:
                file_url = file_info.get("url")
                file_name = file_info.get("name", "unnamed_file")
                
                if not file_url:
                    logger.warning(f"Пропущен файл без URL: {file_name}")
                    continue
                
                output_file = output_directory / file_name
                
                # Потоковая загрузка
                async with client.stream('GET', file_url) as response:
                    response.raise_for_status()
                    async with aiofiles.open(output_file, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=65536):
                            await f.write(chunk)
                
                # Используем asyncio.to_thread для синхронной операции stat()
                file_size = await asyncio.to_thread(lambda: output_file.stat().st_size)
                total_size += file_size
                size_mb = file_size / (1024 * 1024)
                
                # Используем asyncio.to_thread для absolute()
                file_path = await asyncio.to_thread(lambda: str(output_file.absolute()))
                downloaded_files.append({
                    "name": file_name,
                    "path": file_path,
                    "size_mb": round(size_mb, 2)
                })
                
                # Даём контроль event loop после загрузки файла
                await asyncio.sleep(0)
        
        # Формируем сообщение о результате
        total_size_mb = total_size / (1024 * 1024)
        # Используем asyncio.to_thread для absolute()
        output_dir_abs = await asyncio.to_thread(lambda: output_directory.absolute())
        message = f"✅ Успешно загружено {len(downloaded_files)} файл(ов)!\n\n"
        message += f"📁 Директория: {output_dir_abs}\n"
        message += f"💾 Общий размер: {total_size_mb:.2f} MB\n\n"
        message += "📄 Загруженные файлы:\n"
        
        for file_info in downloaded_files:
            message += f"  • {file_info['name']} ({file_info['size_mb']} MB)\n"
        
        return message
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке результата: {str(e)}")
        return f"❌ Ошибка при загрузке результата: {str(e)}"


def main():
    """Точка входа для запуска MCP сервера"""
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(
        description='Rodin Gen-2 MCP сервер для генерации 3D моделей'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='Путь к файлу для записи детальных логов (например, rodin_server.log)'
    )
    
    args = parser.parse_args()
    
    # Настраиваем логирование в файл, если указан
    if args.log_file:
        setup_logging(args.log_file)
    
    logger.info("Запуск Rodin Gen-2 MCP сервера...")
    
    # Проверяем наличие API ключа
    if not RODIN_API_KEY:
        logger.error(
            "RODIN_API_KEY не установлен! "
            "Пожалуйста, создайте .env файл с RODIN_API_KEY=your_api_key"
        )
    else:
        logger.debug(f"RODIN_API_KEY настроен (length={len(RODIN_API_KEY)})")
    
    logger.debug(f"API Base URL: {RODIN_API_BASE_URL}")
    
    # Запускаем сервер
    mcp.run()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Прямое тестирование функции загрузки без MCP протокола
"""

import asyncio
import sys
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Импортируем функцию загрузки напрямую
from rodin_gen2_server import _download_result_background, download_tasks, get_download_lock


async def test_download():
    """Тестирует загрузку модели напрямую"""
    
    # UUID первой модели из ваших логов
    task_uuid = "df42e8cc-1791-45f9-b1f1-9512bb50b120"
    output_dir = "test_downloads"
    task_id = "test-download-001"
    
    print("=" * 60)
    print("🧪 ТЕСТ ПРЯМОЙ ЗАГРУЗКИ МОДЕЛИ")
    print("=" * 60)
    print(f"📦 Task UUID: {task_uuid}")
    print(f"📁 Output dir: {output_dir}")
    print(f"🆔 Task ID: {task_id}")
    print("=" * 60)
    print()
    
    # Регистрируем задачу в глобальном словаре
    async with get_download_lock():
        download_tasks[task_id] = {
            "status": "pending",
            "task_uuid": task_uuid,
            "output_dir": output_dir,
            "files": [],
            "error": None
        }
    
    print("⏳ Запуск загрузки...")
    print()
    
    try:
        # Запускаем загрузку с таймаутом в 60 секунд
        await asyncio.wait_for(
            _download_result_background(task_uuid, output_dir, task_id),
            timeout=60.0
        )
        
        print()
        print("=" * 60)
        print("✅ ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        
        # Проверяем статус
        async with get_download_lock():
            task_info = download_tasks.get(task_id)
            if task_info:
                print(f"📊 Статус: {task_info['status']}")
                print(f"📁 Файлов загружено: {len(task_info.get('files', []))}")
                
                if task_info.get('error'):
                    print(f"❌ Ошибка: {task_info['error']}")
                
                if task_info.get('files'):
                    print("\n📦 Загруженные файлы:")
                    for file_info in task_info['files']:
                        print(f"   • {file_info['name']} ({file_info['size_mb']} MB)")
        
        return True
        
    except asyncio.TimeoutError:
        print()
        print("=" * 60)
        print("⏱️ ТАЙМАУТ! ЗАГРУЗКА ЗАВИСЛА!")
        print("=" * 60)
        print("❌ Загрузка не завершилась за 60 секунд")
        
        # Проверяем статус
        async with get_download_lock():
            task_info = download_tasks.get(task_id)
            if task_info:
                print(f"📊 Последний статус: {task_info['status']}")
                if task_info.get('error'):
                    print(f"❌ Ошибка: {task_info['error']}")
        
        return False
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ОШИБКА ПРИ ЗАГРУЗКЕ!")
        print("=" * 60)
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Сообщение: {str(e)}")
        
        import traceback
        print("\n🔍 Traceback:")
        traceback.print_exc()
        
        return False


async def test_multiple_downloads():
    """Тестирует параллельные загрузки"""
    print("=" * 60)
    print("🧪 ТЕСТ ПАРАЛЛЕЛЬНЫХ ЗАГРУЗОК")
    print("=" * 60)
    print()
    
    tasks = [
        ("df42e8cc-1791-45f9-b1f1-9512bb50b120", "test_downloads/model1", "test-001"),
        ("c799eb71-3e74-4a4a-bfc2-1e0c246ef445", "test_downloads/model2", "test-002"),
    ]
    
    # Регистрируем задачи
    for task_uuid, output_dir, task_id in tasks:
        async with get_download_lock():
            download_tasks[task_id] = {
                "status": "pending",
                "task_uuid": task_uuid,
                "output_dir": output_dir,
                "files": [],
                "error": None
            }
    
    print(f"📦 Запуск {len(tasks)} параллельных загрузок...")
    print()
    
    try:
        # Запускаем все загрузки параллельно
        download_coros = [
            _download_result_background(task_uuid, output_dir, task_id)
            for task_uuid, output_dir, task_id in tasks
        ]
        
        await asyncio.wait_for(
            asyncio.gather(*download_coros, return_exceptions=True),
            timeout=120.0
        )
        
        print()
        print("=" * 60)
        print("✅ ВСЕ ЗАГРУЗКИ ЗАВЕРШЕНЫ!")
        print("=" * 60)
        return True
        
    except asyncio.TimeoutError:
        print()
        print("=" * 60)
        print("⏱️ ТАЙМАУТ! ЗАГРУЗКИ ЗАВИСЛИ!")
        print("=" * 60)
        return False


if __name__ == "__main__":
    print("\n🚀 Начало тестирования...\n")
    
    # Выбор теста
    if len(sys.argv) > 1 and sys.argv[1] == "multiple":
        result = asyncio.run(test_multiple_downloads())
    else:
        result = asyncio.run(test_download())
    
    print()
    if result:
        print("✅ Тест пройден успешно!")
        sys.exit(0)
    else:
        print("❌ Тест провален!")
        sys.exit(1)

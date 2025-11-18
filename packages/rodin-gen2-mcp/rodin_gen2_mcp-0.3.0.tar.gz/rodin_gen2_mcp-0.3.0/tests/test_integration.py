#!/usr/bin/env python3
"""
Интеграционные тесты для Rodin Gen-2 MCP сервера
Проверяют отзывчивость сервера при фоновых операциях
"""

import asyncio
import pytest
import time
from pathlib import Path
import sys

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent.parent))

from rodin_gen2_server import (
    check_download_result_status,
    download_tasks,
    get_download_lock,
    get_download_semaphore,
    _download_result_background
)


class TestMCPResponsiveness:
    """Тесты отзывчивости MCP сервера"""
    
    @pytest.mark.asyncio
    async def test_check_status_without_background_task(self):
        """Тест: check_download_result_status работает без фоновых задач"""
        start_time = time.time()
        result = await check_download_result_status("non-existent-id")
        elapsed = time.time() - start_time
        
        assert "не найдена" in result
        assert elapsed < 0.1, f"Запрос занял {elapsed:.2f}s, ожидалось < 0.1s"
        print(f"✅ Базовый запрос: {elapsed:.3f}s")
    
    @pytest.mark.asyncio
    async def test_check_status_with_pending_task(self):
        """Тест: check_download_result_status работает с pending задачей"""
        # Создаём pending задачу
        task_id = "test-task-pending"
        async with get_download_lock():
            download_tasks[task_id] = {
                "status": "pending",
                "error": None,
                "files": [],
                "output_dir": None,
                "total_size_mb": 0.0,
            }
        
        start_time = time.time()
        result = await check_download_result_status(task_id)
        elapsed = time.time() - start_time
        
        assert "очередь" in result
        assert elapsed < 0.1, f"Запрос занял {elapsed:.2f}s, ожидалось < 0.1s"
        print(f"✅ Запрос с pending задачей: {elapsed:.3f}s")
        
        # Очистка
        async with get_download_lock():
            download_tasks.pop(task_id, None)
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_status_checks(self):
        """Тест: множественные одновременные проверки статуса"""
        task_id = "test-task-concurrent"
        async with get_download_lock():
            download_tasks[task_id] = {
                "status": "running",
                "error": None,
                "files": [],
                "output_dir": None,
                "total_size_mb": 0.0,
            }
        
        # Запускаем 10 одновременных проверок
        start_time = time.time()
        tasks = [
            check_download_result_status(task_id)
            for _ in range(10)
        ]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time
        
        assert all("выполняется" in r for r in results)
        assert elapsed < 0.5, f"10 запросов заняли {elapsed:.2f}s, ожидалось < 0.5s"
        print(f"✅ 10 одновременных запросов: {elapsed:.3f}s")
        
        # Очистка
        async with get_download_lock():
            download_tasks.pop(task_id, None)
    
    @pytest.mark.asyncio
    async def test_status_check_during_simulated_background_work(self):
        """Тест: проверка статуса во время симулированной фоновой работы"""
        task_id = "test-task-simulated"
        
        async def simulate_heavy_background_work():
            """Симулирует тяжёлую фоновую работу"""
            async with get_download_semaphore():
                async with get_download_lock():
                    download_tasks[task_id] = {
                        "status": "running",
                        "error": None,
                        "files": [],
                        "output_dir": None,
                        "total_size_mb": 0.0,
                    }
                
                # Симулируем загрузку с yield points
                for i in range(100):
                    await asyncio.sleep(0.01)  # Симулируем I/O
                    if i % 10 == 0:
                        await asyncio.sleep(0)  # Yield point
                
                async with get_download_lock():
                    download_tasks[task_id]["status"] = "completed"
        
        # Запускаем фоновую работу
        bg_task = asyncio.create_task(simulate_heavy_background_work())
        
        # Ждём немного, чтобы фоновая работа началась
        await asyncio.sleep(0.05)
        
        # Проверяем отзывчивость во время работы
        status_checks = []
        for _ in range(5):
            start_time = time.time()
            result = await check_download_result_status(task_id)
            elapsed = time.time() - start_time
            status_checks.append(elapsed)
            assert elapsed < 0.2, f"Запрос занял {elapsed:.2f}s во время фоновой работы"
            await asyncio.sleep(0.1)
        
        # Ждём завершения фоновой задачи
        await bg_task
        
        avg_time = sum(status_checks) / len(status_checks)
        print(f"✅ Отзывчивость во время фоновой работы: среднее {avg_time:.3f}s")
        
        # Очистка
        async with get_download_lock():
            download_tasks.pop(task_id, None)
    
    @pytest.mark.asyncio
    async def test_event_loop_starvation(self):
        """Тест: обнаружение голодания event loop"""
        
        async def cpu_intensive_task():
            """Задача без yield points - плохой пример"""
            result = 0
            for i in range(1000000):
                result += i
            return result
        
        async def responsive_task():
            """Задача с yield points - хороший пример"""
            result = 0
            for i in range(1000000):
                result += i
                if i % 10000 == 0:
                    await asyncio.sleep(0)
            return result
        
        # Тест с CPU-intensive задачей
        start = time.time()
        task1 = asyncio.create_task(cpu_intensive_task())
        await asyncio.sleep(0.01)  # Даём задаче начаться
        
        # Пытаемся выполнить быстрый запрос
        check_start = time.time()
        result = await check_download_result_status("test")
        check_time = time.time() - check_start
        
        await task1
        total_time = time.time() - start
        
        print(f"⚠️  CPU-intensive: проверка статуса заняла {check_time:.3f}s")
        
        # Тест с responsive задачей
        start = time.time()
        task2 = asyncio.create_task(responsive_task())
        await asyncio.sleep(0.01)
        
        check_start = time.time()
        result = await check_download_result_status("test")
        check_time_responsive = time.time() - check_start
        
        await task2
        total_time_responsive = time.time() - start
        
        print(f"✅ Responsive: проверка статуса заняла {check_time_responsive:.3f}s")
        
        assert check_time_responsive < check_time, "Responsive задача должна быть быстрее"


class TestBackgroundTaskIsolation:
    """Тесты изоляции фоновых задач"""
    
    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrent_tasks(self):
        """Тест: семафор ограничивает количество одновременных задач"""
        
        counter = {"running": 0, "max_concurrent": 0}
        
        async def tracked_task(task_num: int):
            async with get_download_semaphore():
                counter["running"] += 1
                counter["max_concurrent"] = max(counter["max_concurrent"], counter["running"])
                await asyncio.sleep(0.1)
                counter["running"] -= 1
        
        # Запускаем 5 задач с семафором=1
        tasks = [tracked_task(i) for i in range(5)]
        await asyncio.gather(*tasks)
        
        assert counter["max_concurrent"] == 1, f"Семафор не ограничил: {counter['max_concurrent']} одновременных"
        print(f"✅ Семафор работает: максимум {counter['max_concurrent']} одновременная задача")


async def run_diagnostic_suite():
    """Запускает полный набор диагностических тестов"""
    print("=" * 70)
    print("🔍 ДИАГНОСТИКА ОТЗЫВЧИВОСТИ MCP СЕРВЕРА")
    print("=" * 70)
    
    test_suite = TestMCPResponsiveness()
    
    print("\n📋 Тест 1: Базовая отзывчивость")
    await test_suite.test_check_status_without_background_task()
    
    print("\n📋 Тест 2: Отзывчивость с pending задачей")
    await test_suite.test_check_status_with_pending_task()
    
    print("\n📋 Тест 3: Множественные одновременные запросы")
    await test_suite.test_multiple_concurrent_status_checks()
    
    print("\n📋 Тест 4: Отзывчивость во время фоновой работы")
    await test_suite.test_status_check_during_simulated_background_work()
    
    print("\n📋 Тест 5: Обнаружение голодания event loop")
    await test_suite.test_event_loop_starvation()
    
    print("\n📋 Тест 6: Изоляция фоновых задач через семафор")
    bg_tests = TestBackgroundTaskIsolation()
    await bg_tests.test_semaphore_limits_concurrent_tasks()
    
    print("\n" + "=" * 70)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
    print("=" * 70)


if __name__ == "__main__":
    print("Запуск диагностических тестов...\n")
    asyncio.run(run_diagnostic_suite())

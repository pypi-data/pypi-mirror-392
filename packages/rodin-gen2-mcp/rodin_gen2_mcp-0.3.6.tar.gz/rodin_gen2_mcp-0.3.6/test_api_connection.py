#!/usr/bin/env python3
"""
Диагностический скрипт для проверки соединения с Rodin API
"""

import asyncio
import time
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

RODIN_API_BASE_URL = "https://api.hyper3d.com/api/v2"
RODIN_API_KEY = os.getenv("RODIN_API_KEY")


async def test_api_connection():
    """Тестирует соединение с Rodin API"""
    print("🔍 Тестирование соединения с Rodin API...")
    print(f"📍 URL: {RODIN_API_BASE_URL}")
    print(f"🔑 API Key: {'✅ установлен' if RODIN_API_KEY else '❌ не установлен'}")
    print()
    
    if not RODIN_API_KEY:
        print("❌ RODIN_API_KEY не установлен!")
        return
    
    # Тест 1: Простое TCP соединение
    print("1️⃣ Тест TCP соединения...")
    start = time.time()
    try:
        timeout_config = httpx.Timeout(
            connect=10.0,
            read=30.0,
            write=30.0,
            pool=5.0
        )
        
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            # Простой GET запрос (может вернуть 404, но это нормально)
            response = await client.get(
                f"{RODIN_API_BASE_URL}/test",
                headers={"Authorization": f"Bearer {RODIN_API_KEY}"}
            )
            elapsed = time.time() - start
            print(f"   ✅ TCP+TLS соединение установлено за {elapsed:.2f}s")
            print(f"   📡 Статус ответа: {response.status_code}")
            
    except httpx.TimeoutException as e:
        elapsed = time.time() - start
        print(f"   ⏱️ Таймаут после {elapsed:.2f}s: {e}")
        print("   💡 Возможные причины:")
        print("      - Медленное интернет-соединение")
        print("      - API сервер недоступен")
        print("      - Firewall блокирует соединение")
        return
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"   ❌ Ошибка после {elapsed:.2f}s: {e}")
        return
    
    # Тест 2: Запрос к /download endpoint
    print("\n2️⃣ Тест /download endpoint...")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            response = await client.post(
                f"{RODIN_API_BASE_URL}/download",
                headers={"Authorization": f"Bearer {RODIN_API_KEY}"},
                data={"task_uuid": "test-uuid-12345"}
            )
            elapsed = time.time() - start
            print(f"   ✅ Запрос выполнен за {elapsed:.2f}s")
            print(f"   📡 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ API отвечает корректно!")
            else:
                print(f"   ℹ️ Ответ: {response.text[:200]}")
                
    except httpx.TimeoutException as e:
        elapsed = time.time() - start
        print(f"   ⏱️ Таймаут после {elapsed:.2f}s: {e}")
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"   ℹ️ Ожидаемая ошибка (тестовый UUID): {str(e)[:200]}")
    
    print("\n✅ Диагностика завершена!")


if __name__ == "__main__":
    asyncio.run(test_api_connection())

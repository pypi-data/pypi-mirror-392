#!/usr/bin/env python3
"""
Скрипт для запуска тестов с различными опциями
"""
import sys
import subprocess
import argparse


def run_tests(coverage=False, verbose=False, specific_test=None, html_report=False):
    """Запускает тесты с заданными параметрами"""
    
    cmd = ["pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=.",
            "--cov-report=term-missing",
        ])
        
        if html_report:
            cmd.append("--cov-report=html")
    
    if specific_test:
        cmd.append(specific_test)
    
    print(f"Запуск команды: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем")
        return 130
    except Exception as e:
        print(f"\n\nОшибка при запуске тестов: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Запуск тестов для Rodin Gen-2 MCP Server"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Запустить с измерением покрытия кода"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Подробный вывод"
    )
    
    parser.add_argument(
        "-t", "--test",
        type=str,
        help="Запустить конкретный тест (например, tests/test_main.py)"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="Создать HTML отчет о покрытии (требует --coverage)"
    )
    
    args = parser.parse_args()
    
    if args.html and not args.coverage:
        print("⚠️  Опция --html требует --coverage")
        args.coverage = True
    
    exit_code = run_tests(
        coverage=args.coverage,
        verbose=args.verbose,
        specific_test=args.test,
        html_report=args.html
    )
    
    if exit_code == 0:
        print("\n✅ Все тесты прошли успешно!")
        if args.coverage and args.html:
            print("📊 HTML отчет о покрытии: htmlcov/index.html")
    else:
        print(f"\n❌ Тесты завершились с ошибкой (код: {exit_code})")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

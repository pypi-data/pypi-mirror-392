#!/usr/bin/env python3
"""Скрипт для просмотра примеров из папки examples."""

import os
from pathlib import Path


def show_examples():
    """Показывает список примеров и выводит выбранный."""
    examples_dir = Path(__file__).parent / "examples"

    # Получаем список .lua файлов
    examples = sorted([f for f in examples_dir.glob("*.lua")])

    if not examples:
        print("Примеры не найдены в папке examples/")
        return

    # Показываем список примеров
    print("\n=== Доступные примеры ===\n")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example.name}")

    print("\n" + "=" * 25 + "\n")

    # Получаем выбор пользователя
    while True:
        try:
            choice = input(
                f"Выберите пример (1-{len(examples)}) или 'q' для выхода: "
            ).strip()

            if choice.lower() == "q":
                print("Выход...")
                break

            choice_num = int(choice)

            if 1 <= choice_num <= len(examples):
                selected_file = examples[choice_num - 1]
                print(f"\n{'=' * 60}")
                print(f"Пример: {selected_file.name}")
                print("=" * 60 + "\n")

                # Читаем и выводим содержимое файла
                with open(selected_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(content)

                print(f"\n{'=' * 60}\n")
            else:
                print(f"Ошибка: выберите число от 1 до {len(examples)}")

        except ValueError:
            print("Ошибка: введите число или 'q' для выхода")
        except KeyboardInterrupt:
            print("\n\nВыход...")
            break
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    show_examples()

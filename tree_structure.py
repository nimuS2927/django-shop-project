"""
tree_limited.py — выводит дерево файлов и папок с ограничением по глубине вложенности.
Скрытые файлы название которых начинается с "." пропускаются всегда.

Использование:
    python tree_limited.py [путь] [опции]

Опции:
    --max-level N              Максимальная глубина вложенности (по умолчанию: 2)
    --exclude name1 name2      Исключить указанные файлы/папки (папки отображаются, но не раскрываются)
    --exclude-group GROUP      Предустановленная группа исключений (common, python)
    --output filename.txt      Сохранить вывод в файл (если не указано — вывод в консоль)

Примеры:
    python tree_limited.py . --max-level 3
    python tree_limited.py . --exclude .venv secrets.json
    python tree_limited.py . --exclude-group common --output tree.txt

Предустановленные группы:
    common    → venv, git, __pycache__, idea, node_modules, migrations
    python    → __pycache__, .pytest_cache, .mypy_cache
"""

import os

EXCLUDE_GROUPS = {
    "common": {"venv", "__pycache__", "git", "idea", "migrations"},
    "python": {"__pycache__", ".pytest_cache", ".mypy_cache"},
}


def print_tree(start_path, max_level=4, current_level=0, prefix='', excluded=None, output=None):
    if current_level >= max_level:
        return

    # Получаем содержимое текущей директории, которое подлежит обработке
    entries = sorted(os.listdir(start_path))
    entries = [e for e in entries if not e.startswith('.')]  # Пропуск скрытых файлов
    entries = [e for e in entries if e not in excluded]      # Пропуск исключённых файлов

    # Обрабатываем содержимое текущей директории
    for i, name in enumerate(entries):
        path = os.path.join(start_path, name)
        is_dir = os.path.isdir(path)
        connector = '└── ' if i == len(entries) - 1 else '├── '

        output.append(prefix + connector + name)
        # Если текущий путь это директория, то запускаем рекурсивно ее обработку
        if is_dir and name not in excluded:
            extension = '    ' if i == len(entries) - 1 else '│   '
            print_tree(path, max_level, current_level + 1, prefix + extension, excluded, output)


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Вывод структуры каталогов в виде дерева.')
    parser.add_argument('start_path', nargs='?', default='.', help='Начальная директория')
    parser.add_argument('--max-level', type=int, default=4, help='Максимальный уровень вложенности')
    parser.add_argument('--exclude', nargs='*', default=[], help='Исключённые файлы/папки')
    parser.add_argument('--exclude-group', choices=EXCLUDE_GROUPS.keys(), help='Предустановленная группа исключений')
    parser.add_argument('--output', help='Файл для записи (если не указан — вывод в консоль)')

    args = parser.parse_args()

    excluded = set(args.exclude)
    if args.exclude_group:
        excluded |= EXCLUDE_GROUPS[args.exclude_group]

    output_lines = []
    print_tree(args.start_path, args.max_level, excluded=excluded, output=output_lines)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print(f"Дерево сохранено в файл: {args.output}")
    else:
        print('\n'.join(output_lines))


if __name__ == "__main__":
    main()

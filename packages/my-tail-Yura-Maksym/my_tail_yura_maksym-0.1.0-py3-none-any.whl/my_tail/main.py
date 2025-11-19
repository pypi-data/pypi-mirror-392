import click
import time
import sys
from collections import deque


@click.command()
@click.option(
    '--lines', '-n',
    type=int,
    default=10,
    show_default=True,  # Показувати значення за замовчуванням у --help
    help='Кількість рядків для виводу.'
)
@click.option(
    '--follow', '-f',
    is_flag=True,
    help='Слідкувати за файлом та виводити нові рядки.'
)
@click.argument(
    'file_path',
    type=click.Path(exists=True, dir_okay=False, readable=True)
)
def my_tail(file_path, lines, follow):
    """
    Проста реалізація утиліти tail на Python.

    Виводить останні N рядків з FILE.
    З прапором -f, виводить нові рядки, що додаються у файл.
    """
    try:
        # 'encoding="utf-8"' важливо для Windows та кирилиці
        with open(file_path, 'r', encoding='utf-8') as f:
            # 1. Ефективно читаємо останні N рядків
            # deque(f, maxlen=N) автоматично збереже лише N останніх рядків
            last_lines = deque(f, maxlen=lines)

            # Виводимо їх
            for line in last_lines:
                print(line, end='')

            # 2. Якщо вказано -f, переходимо в режим "слідкування"
            if follow:
                # Файловий вказівник вже в кінці файлу (завдяки deque)
                while True:
                    line = f.readline()
                    if not line:
                        # Якщо нових рядків немає, чекаємо трохи
                        time.sleep(0.1)
                        continue
                    # Якщо з'явився новий рядок, друкуємо його
                    print(line, end='')

    except FileNotFoundError:
        print(f"Помилка: Файл не знайдено '{file_path}'", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        # Дозволяємо користувачу вийти з режиму -f (Ctrl+C)
        sys.exit(0)
    except Exception as e:
        print(f"Сталася помилка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    my_tail()
import click  # Імпортуємо бібліотеку, яку щойно встановили
import sys    # Потрібен для роботи з помилками та stdin

def sort_key_numeric(line):
    """Допоміжна функція для числового сортування."""
    try:
        # Спробуємо перетворити очищений рядок на float (число)
        return float(line.strip())
    except ValueError:
        # Якщо це не число (наприклад, "abc"),
        # повертаємо 0, щоб сортування не зламалось
        return 0.0

@click.command()
@click.option(
    '--reverse', '-r',
    is_flag=True,  # Це прапор, він або є, або нема
    help='Сортувати у зворотному порядку.'
)
@click.option(
    '--numeric', '-n',
    is_flag=True,
    help='Сортувати як числа, а не як текст.'
)
@click.argument(
    'file',
    type=click.File('r'), # 'r' - відкрити для читання
    default='-'  # '-' означає stdin (стандартний ввід)
)
def my_sort(file, reverse, numeric):
    """
    Проста реалізація утиліти sort на Python.

    Читає рядки з FILE (або стандартного вводу, якщо FILE не вказано)
    і виводить їх у відсортованому порядку.
    """
    try:
        # Читаємо всі рядки з файлу (або stdin)
        lines = file.readlines()
    except Exception as e:
        print(f"Помилка читання файлу: {e}", file=sys.stderr)
        sys.exit(1) # Вийти з програми з кодом помилки

    # Визначаємо, за яким "ключем" (правилом) сортувати
    if numeric:
        # Якщо є прапор -n, використовуємо нашу числову функцію
        sort_key = sort_key_numeric
    else:
        # Інакше просто сортуємо як текст (alpha-numeric)
        sort_key = lambda line: line.strip()

    # Сортуємо!
    try:
        sorted_lines = sorted(lines, key=sort_key, reverse=reverse)
    except Exception as e:
        print(f"Помилка під час сортування: {e}", file=sys.stderr)
        sys.exit(1)

    # Виводимо результат
    for line in sorted_lines:
        print(line, end='') # end='' прибирає зайві нові рядки

if __name__ == '__main__':
    my_sort()

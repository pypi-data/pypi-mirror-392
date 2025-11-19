# my_sort/cli.py
import sys
import click
from typing import List, Iterable


def read_lines_from_files(files: List[str]) -> Iterable[str]:
    if not files:
        for line in sys.stdin:
            yield line.rstrip('\n')
    else:
        for fname in files:
            if fname == '-':
                for line in sys.stdin:
                    yield line.rstrip('\n')
            else:
                try:
                    with open(fname, 'r', encoding='utf-8') as f:
                        for line in f:
                            yield line.rstrip('\n')
                except FileNotFoundError:
                    click.echo(f"my-sort: cannot open '{fname}': No such file or directory", err=True)


def try_float(s: str):
    try:
        return float(s)
    except Exception:
        return None


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-r', '--reverse', is_flag=True, help='Виводити рядки в зворотному порядку.')
@click.option('-n', '--numeric', 'numeric', is_flag=True, help='Порівнювати як числа (numeric sort).')
@click.argument('files', nargs=-1, type=click.Path(exists=False))
def cli(reverse: bool, numeric: bool, files: List[str]):
    """
    my-sort — проста реалізація sort з опціями -r та -n.

    Якщо не задано файлів, читає зі stdin.
    Можна передати '-' як ім'я файлу для stdin.
    """
    lines = list(read_lines_from_files(list(files)))
    if numeric:
        # При numeric: спробувати перетворити на float, якщо не вдається — використовувати рядок як запасний ключ
        def key_func(x):
            fx = try_float(x.strip())
            return (0, fx) if fx is not None else (1, x)
    else:
        key_func = lambda x: x

    try:
        lines.sort(key=key_func, reverse=reverse)
    except Exception as e:
        # На випадок, якщо порівняння несподівано впаде
        click.echo(f"my-sort: error while sorting: {e}", err=True)
        sys.exit(1)

    for line in lines:
        click.echo(line)


if __name__ == '__main__':
    cli()

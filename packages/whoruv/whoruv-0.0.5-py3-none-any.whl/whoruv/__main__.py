from whoruv import __version__
from whoruv._core import format_python_info, whoruv


def main() -> None:
    print(f"whoruv v{__version__}\n")
    print(format_python_info(whoruv()))


if __name__ == "__main__":
    main()

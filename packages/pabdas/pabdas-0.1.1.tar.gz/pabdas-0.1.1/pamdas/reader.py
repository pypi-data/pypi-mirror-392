from importlib.resources import files

DATA_PKG = "pamdas.data"


def ls():
    """List bundled .txt files."""
    data = files(DATA_PKG)
    return [p.name for p in data.iterdir() if p.suffix == ".txt"]


def read(name: str) -> str:
    """Read a single text file's contents."""
    data = files(DATA_PKG)
    f = data / name
    if not f.is_file():
        raise FileNotFoundError(f"No such file: {name}")
    return f.read_text(encoding="utf-8")


def catall():
    """Print all text files."""
    for name in ls():
        print(f"===== {name} =====")
        print(read(name))
        print()

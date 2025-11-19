from importlib.resources import files

def _path(name):
    return files("pabdas.data").joinpath(name)

def ls():
    return [p.name for p in files("pabdas.data").iterdir() if p.is_file()]

import chardet

def read(name: str):
    data = files("pabdas.data")
    f = data / name

    # Read raw bytes first
    raw = f.read_bytes()

    # Auto-detect encoding
    encoding = chardet.detect(raw)["encoding"] or "utf-8"

    # Decode safely
    return raw.decode(encoding, errors="replace")


def catall():
    for name in ls():
        print("===== ", name, " =====")
        print(read(name))
        print()

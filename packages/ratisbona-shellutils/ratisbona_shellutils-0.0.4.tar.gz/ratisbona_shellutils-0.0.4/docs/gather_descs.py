from pathlib import Path

from ratisbona_utils.strings import indent

from ratisbona_utils.io import UTF8

from ratisbona_utils.monads import Maybe, Nothing, Just


def try_get_desc(path: Path) -> Maybe[str]:
    init_path = path / "__init__.py"
    if init_path.exists():
        return Just(init_path.read_text(**UTF8).replace('"""', ""))
    return Nothing


def main():
    src_path = Path(__file__).parent.parent / "src"

    descs = ""
    for package_file in src_path.iterdir():
        for subpackage in package_file.iterdir():
            if subpackage.is_dir():
                if maybe_desc := try_get_desc(subpackage):
                    descs += subpackage.name + ": " + indent(maybe_desc.unwrap_value(), 2)

    print(descs)


if __name__ == "__main__":
    main()

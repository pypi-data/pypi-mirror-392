class Color:
    def __init__(self, r: int, g: int, b: int) -> None:
        pass

    @staticmethod
    def from_rgb16(raw: int) -> Color:
        pass

    def to_rgb16(self) -> int:
        pass

    def to_rgb(self) -> tuple[int, int, int]:
        pass


class Runner:
    """Manually written type stubs for the Runner. defined in Rust.

    Since it's kept in sync manually, type errors in the runtime are possible.
    However, having a stub like this helps to have semantic syntax highligting,
    autocomplete, and other static analysis goodies.
    """

    def __init__(
        self,
        author_id: str,
        app_id: str,
        vfs_path: str,
    ) -> None:
        """Initalizes the Runner and the wrapped Runtime.

        It includes reading and parsing wasm module, validating ROM, etc.
        """
        pass

    def start(self) -> None:
        pass

    def update(self) -> bool:
        pass

    def get_frame(self) -> list[int]:
        pass

    def set_input(self, x: int, y: int, b: int) -> None:
        pass

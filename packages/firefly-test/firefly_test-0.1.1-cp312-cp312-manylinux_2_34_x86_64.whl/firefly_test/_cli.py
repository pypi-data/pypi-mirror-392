from __future__ import annotations

import subprocess
from pathlib import Path


class CLI:
    """A wrapper around firefly_cli.
    """
    __slots__ = ['_bin', '_vfs']
    _vfs: Path | None
    _bin: str

    def __init__(
        self, *,
        vfs: Path | None = None,
        binary: str = 'firefly_cli',
    ) -> None:
        self._vfs = vfs
        self._bin = binary

    def build(self, root: Path | None = None) -> None:
        if root is None:
            root = Path()
        self._run(str(root.resolve()))

    def _run(self, *args: str) -> None:
        cmd = [self._bin]
        if self._vfs is not None:
            cmd.extend(['--vfs', str(self._vfs)])
        cmd.append('build')
        cmd.extend(args)
        subprocess.run(cmd, check=True)

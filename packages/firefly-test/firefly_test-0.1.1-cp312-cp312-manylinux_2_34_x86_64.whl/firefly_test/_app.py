from __future__ import annotations

from pathlib import Path
from typing import Iterator

import firefly_test._rust as rust

from ._frame import Frame
from ._input import Input


class ExitedError(Exception):
    """Raised from Firefly.update if the app exits.
    """
    pass


class App:
    """A runtime for a single Firefly Zero app.

    Args:
        id: the full ID of the app. For example, "lux.snek".
        vfs_path: optional Path to the virtual FS root.
            If not specified, the global one is detected automatically.
    """
    __slots__ = (
        '_app_id',
        '_author_id',
        '_exited',
        '_runner',
        '_started',
        '_vfs_path',
    )
    _runner: rust.Runner
    _author_id: str
    _app_id: str
    _vfs_path: Path
    _started: bool
    _exited: bool

    def __init__(
        self,
        id: str | tuple[str, str],
        vfs_path: Path | None = None,
    ) -> None:
        if isinstance(id, str):
            left, sep, right = id.partition('.')
            assert sep == '.'
            id = (left, right)
        self._author_id, self._app_id = id
        assert 0 < len(self._author_id) <= 16
        assert 0 < len(self._app_id) <= 16
        self._started = False
        self._exited = False
        self._runner = rust.Runner(
            author_id=self._author_id,
            app_id=self._app_id,
            vfs_path=str(vfs_path.resolve()) if vfs_path else '',
        )

    def start(self) -> None:
        """Start the app: initialize memory, call `_boot`, etc.
        """
        if self._exited:
            raise RuntimeError('trying to start exited app')
        if self._started:
            raise RuntimeError('trying to start already started app')
        self._started = True
        self._runner.start()

    def update(self, input: Input | None = None) -> None:
        """Run a single update cycle: call `update`, maybe `render`, render menu, etc.

        If no input provided, the old input stays active.

        Raises:
            ExitedError:
        """
        if not self._started:
            raise RuntimeError('app must be started before it can be updated')
        if self._exited:
            raise RuntimeError('trying to update exited app')
        if input is not None:
            self._runner.set_input(
                x=input._pad._x if input._pad else 0xFF,
                y=input._pad._y if input._pad else 0xFF,
                b=input._buttons,
            )
        exit = self._runner.update()
        if exit:
            self._exited = True
            raise ExitedError

    @property
    def frame(self) -> Frame:
        """Get the image currently rendered on the virtual mock screen.
        """
        if not self._started:
            raise RuntimeError('the app is not started, nothing is displayed')
        buf = self._runner.get_frame()
        return Frame._from_rgb16(buf, width=240)

    def __iter__(self) -> Iterator[Frame]:
        """Start the app if needed and on each iteration cycle update it and get Frame.
        """
        if not self._started:
            self.start()
        while True:
            try:
                self.update()
            except ExitedError:
                return
            yield self.frame

    def __repr__(self) -> str:
        id = f'{self._author_id}.{self._app_id}'
        return f"{type(self).__name__}('{id}')"

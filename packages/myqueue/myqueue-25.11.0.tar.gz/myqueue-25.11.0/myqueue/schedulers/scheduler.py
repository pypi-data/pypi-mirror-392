from __future__ import annotations

import os
from pathlib import Path
import warnings

from myqueue.config import Configuration
from myqueue.task import Task
from myqueue.resources import Resources


class Scheduler:
    def __init__(self, config: Configuration):
        self.config = config
        self.name = config.scheduler.lower()
        venv = os.environ.get('VIRTUAL_ENV')
        self.activation_script = (Path(venv) / 'bin/activate'
                                  if venv is not None else None)

    def preamble(self) -> str:
        lines = []
        if self.activation_script:
            lines += [f'source {self.activation_script}',
                      f'echo "venv: {self.activation_script}"']
        pre = os.environ.get('MYQUEUE_PREAMBLE')
        if pre:
            lines.append(pre.rstrip())
        return '\n'.join(lines)

    def submit(self,
               task: Task,
               dry_run: bool = False,
               verbose: bool = False) -> int:
        """Submit a task."""
        raise NotImplementedError

    def cancel(self, id: int) -> None:
        """Cancel a task."""
        raise NotImplementedError

    def get_ids(self) -> set[int]:
        """Get ids for all tasks the scheduler knows about."""
        raise NotImplementedError

    def hold(self, id: int) -> None:
        raise NotImplementedError

    def release_hold(self, id: int) -> None:
        raise NotImplementedError

    def error_file(self, task: Task) -> Path:
        return task.folder / f'{task.cmd.short_name}.{task.id}.err'

    def has_timed_out(self, task: Task) -> bool:
        path = self.error_file(task).expanduser()
        if path.is_file():
            task.tstop = path.stat().st_mtime
            lines = path.read_text().splitlines()
            for line in lines:
                if line.endswith('DUE TO TIME LIMIT ***'):
                    return True
        return False

    def maxrss(self, id: int) -> int:
        return 0

    def get_config(self, queue: str = '') -> tuple[list[tuple[str, int, str]],
                                                   list[str]]:
        raise NotImplementedError

    def should_we_use_mpi(self, resources: Resources) -> bool:
        """Should we call mpiexec?"""
        if resources.processes == 1:
            warn = (resources.cores > 1 and
                    self.config.use_mpi and
                    resources.serial is None)
            if warn:
                dct = resources.todict()
                dct['serial'] = True
                dct.pop('processes')
                new = Resources(**dct)
                url = 'https://myqueue.readthedocs.io/releasenotes.html'
                warnings.warn(
                    f'The meaning of "{resources}" has changed! '
                    f'Perhaps you should use "{new}" instead? '
                    f'See {url}#version-25-4-0')
            return False
        if resources.serial is None:
            return self.config.use_mpi
        return not resources.serial

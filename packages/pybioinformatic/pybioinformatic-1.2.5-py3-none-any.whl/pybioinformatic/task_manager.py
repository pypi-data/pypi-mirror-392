#!/usr/bin/env python
"""
File: task_manager.py
Description: Instance a TaskManager.
CreateDate: 2023/9/8
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Union, Tuple, Iterable, Callable, Generator
from os import getcwd
from subprocess import run, PIPE
from datetime import datetime
from getpass import getuser
from socket import gethostname
import multiprocessing
from click import echo


class TaskManager:
    def __init__(
        self,
        commands: Iterable[str] = None,
        num_processing: int = None,
        params: Iterable[tuple] = None
    ):
        try:
            self.task = list(commands)
        except TypeError:
            self.task = []
        self.params = params
        self.num_processing = num_processing

    def add_task(self, command: Union[str, Iterable[str]]):
        if isinstance(command, str):
            self.task.append(command)
        else:
            command = list(command)
            self.task.extend(command)

    def del_task(self, index: Union[int, str] = None):
        if isinstance(index, int):
            del self.task[index]
        elif isinstance(index, str):
            self.task.remove(index)
        else:
            self.task.pop()

    def clear_task(self):
        self.task = []

    @staticmethod
    def echo_and_exec_cmd(
        cmd: str,
        show_cmd: bool = True,
        pipe: bool = True
    ) -> Union[Tuple[str, str], None]:
        if show_cmd:
            echo(
                f'\033[33m[{getuser()}@{gethostname()}: '
                f'{datetime.now().replace(microsecond=0)} {getcwd()}]\n$ '
                f'\033[0m\033[36m{cmd}\033[0m', err=True
            )
        if pipe:
            ret = run(cmd, shell=True, executable="/bin/bash", stdout=PIPE, stderr=PIPE)
            stdout, stderr = ret.stdout.decode('utf8'), ret.stderr.decode('utf8')
            return stdout, stderr
        else:
            run(cmd, shell=True, executable="/bin/bash")
            return None

    def serial_run_cmd(self, show_cmd: bool = True, pipe: bool = False) -> Generator[Tuple[str, str], None, None]:
        for cmd in self.task:
            yield self.echo_and_exec_cmd(cmd=cmd, show_cmd=show_cmd, pipe=pipe)

    def parallel_run_cmd(self, show_cmd: bool = True, pipe: bool = False) -> list:
        if not self.task:
            echo('\033[31mError: TaskManager has no task.\033[0m', err=True)
            exit()
        results = []
        with multiprocessing.Pool(self.num_processing) as pool:
            for cmd in self.task:
                ret = pool.apply_async(self.echo_and_exec_cmd, args=(cmd, show_cmd, pipe))
                results.append(ret)
            pool.close()
            pool.join()
        return results

    def parallel_run_func(self, func: Callable, call_back_func: Callable = None):
        results = []
        with multiprocessing.Pool(self.num_processing) as pool:
            for param in self.params:
                ret = pool.apply_async(func, args=param, callback=call_back_func)
                results.append(ret)
            pool.close()
            pool.join()
        return results


if __name__ == '__main__':
    tkm = TaskManager()
    cmds = [f'echo Hello World x {i}' for i in range(10)]
    tkm.add_task(cmds)
    tkm.serial_run_cmd()

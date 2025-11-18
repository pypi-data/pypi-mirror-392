from dataclasses import dataclass
from functools import cached_property, wraps
from getpass import getpass
from pathlib import Path
from typing import Any, Literal

import fabric
import paramiko
from loguru import logger

log = logger.bind(name="ssh")


@dataclass
class System:
    linux: bool = False
    windows: bool = False


class SSH:
    def __init__(self, hostname: str, username: str | None, port: int | None) -> None:
        log.debug("SSH init.")
        self.hostname = hostname
        self.port = port
        self.username = username
        self.con = self.connect()
        # self.sftp = paramiko.SFTPClient.from_transport(self.con.transport)
        self.sftp = self.con.sftp()



    @cached_property
    def system(self) -> System:
        unix_test = self.run("uname -s", hide=True, warn=True)

        if unix_test.ok:
            if "linux" in unix_test.stdout.lower():
                return System(linux=True)
            raise RuntimeError(f"Unsupported system: {unix_test.stdout}")  # noqa: TRY003

        windows_test = self.run("ver", hide=True, warn=True)
        if windows_test.ok:
            if "windows" in windows_test.stdout.lower():
                return System(windows=True)
            raise RuntimeError(f"Unsupported system: {windows_test.stdout}")  # noqa: TRY003

        raise RuntimeError(f"Unknown system.")  # noqa: TRY003

    @cached_property
    def home(self) -> str:
        if self.system.linux:
            return self.run("echo $HOME", hide=True).stdout.strip()
        return self.run(f"powershell -Command \"echo $HOME\"").stdout.strip()

    def resolve_path(self, path: str | Path) -> str:
        path = str(path)

        if path.startswith(("~/", "~\\")):
            path = self.home + path[1:]

        path = path.replace("$HOME", self.home)
        return path if self.system.linux else path.replace("/", "\\")


    def connect(self) -> fabric.Connection:
        try:
            con = fabric.Connection(host=self.hostname, port=self.port, user=self.username)

            con.run("whoami", hide=True)
            log.debug(f"Successfully connected with key file.")
        except paramiko.ssh_exception.AuthenticationException:
            log.debug(f"Failed autentification with key file.")
        except Exception as e:
            log.exception(f"Error connecting. Error: {e}")  # noqa: TRY401
        else:
            return con

        for _ in range(3):
            password = getpass(prompt="Enter password: ")
            try:
                con = fabric.Connection(host=self.hostname, port=self.port, user=self.username,
                                        connect_kwargs={"password": password})
                con.run("whoami", hide=True)
            except paramiko.ssh_exception.AuthenticationException:
                print(f"Incorrect password.")
            except Exception as e:
                print(f"Connection error: {e}")
                raise
            else:
                return con

        raise Exception("Connection error")  # noqa: TRY002, TRY003

        # if  self.system.windows and config is None:
        #     log.debug("Switching to PowerShell")
        #     con = self.connect(
        #         password=password,
        #         config=fabric.Config(overrides={'run': {'shell': 'powershell.exe'}}),
        #     )
        #     con.run("$PSVersionTable.PSEdition", hide=True)


    def check_exist_file(self, path: Path | str) -> bool:
        path = self.resolve_path(path)

        if self.system.linux:
            result = self.run(rf'test -f "{path}"', warn=True, hide=True)
        else:
            result = self.run(
                f"powershell -Command \"Test-Path '{path}' -PathType Leaf\"",
                warn=True, hide=True)

        log.debug(f"{path}\n{result}")
        if self.system.windows and result.stdout.lower().strip() == "false":
            log.debug(f"Windows: {path} doesn't exist")
            return False
        return result.ok

    def check_exist_dir(self, path: Path | str) -> bool:
        path = self.resolve_path(path)

        if self.system.linux:
            result = self.run(rf'test -d "{path}"', warn=True, hide=True)
        else:
            result = self.run(
                f"powershell -Command \"Test-Path '{path}' -PathType Container\"",
                warn=True, hide=True)

        log.debug(f"{path}\n{result}")

        if self.system.windows and result.stdout.lower().strip() == "false":
            log.debug(f"Windows: {path} doesn't exist")
            return False
        return result.ok

    @wraps(fabric.Connection.run)
    def run(self, *args, **kwargs) -> Any:  # noqa: ANN002, ANN003, ANN401
        result = self.con.run(*args, encoding="utf-8", **kwargs)
        if "permission denied" in result.stderr:
            raise PermissionError(result.stderr)
        return result

    # def makedir(self, path: Path | str, exist_ok: bool = True, parents: bool = True) -> bool:
    #     path = self.resolve_path(path)
    #
    #     result = self.run(rf'mkdir "{path!s}"', warn=True, hide=True)
    #
    #     if not result.ok:
    #         if self.check_exist_dir(Path(path).parent):
    #             if exist_ok:
    #                 return True
    #             else:
    #                 raise SystemError(f"Directory {path!s} already exists.")
    #         else:
    #             if parents:
    #                 result = self.run(rf'mkdir -p "{path!s}"', warn=True, hide=True)
    #                 return result.ok
    #             else:
    #                 raise SystemError(f"Parents {path!s} does not exist.")
    #
    #     return result.ok

    def makedir(self, path: Path | str) -> bool:
        path = self.resolve_path(path)

        if self.system == "linux":
            result = self.run(rf'mkdir -p "{path!s}"', warn=True, hide=True)
        else:
            result = self.run(rf'mkdir "{path!s}"', warn=True, hide=True)

        return result.ok

    @wraps(paramiko.SFTPClient.open)
    def open(self, filename: str, *args, **kwargs) -> paramiko.SFTPFile:  # noqa: ANN002, ANN003
        filename = self.resolve_path(filename)
        return self.sftp().open(filename, *args, **kwargs)

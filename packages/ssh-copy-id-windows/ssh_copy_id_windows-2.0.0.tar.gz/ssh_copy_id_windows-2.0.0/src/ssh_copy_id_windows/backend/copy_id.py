import os
from pathlib import Path

from loguru import logger

from .ssh_integration import SSH

log = logger.bind(name="copy_id")

def _list_to_pretty(lst: list) -> str:
    result = ""
    for i, item in enumerate(lst):
        result += f"{i+1}. {item}\n"
    return result

def _resolve_path(path: Path | str) -> Path:
    log.debug(f"{path}")
    path = str(path)

    if path.startswith(("~/", "~\\")):
        path = str(Path.home().absolute() / path[1:].lstrip("/").lstrip("\\"))
        log.debug(f"{path}")

    if "/" not in path and "\\" not in path:
        path = str(Path.home().absolute() / ".ssh" / path)
        log.debug(f"{path}")

    path = Path(path).absolute()
    log.debug(f"{path}")
    return path


def _find_id(path: Path) -> Path:

    if path.is_file():
        with open(path, encoding="utf-8") as f:
            data = f.read()

        if data.startswith("ssh-"):
            return path

        with open(path.parent / f"{path.name}.pub", encoding="utf-8") as f:
            data = f.read()

        if data.startswith("ssh-"):
            return path.parent / f"{path.name}.pub"

        raise FileNotFoundError(path)

    raise FileNotFoundError(f"Path {path} is not file")  # noqa: TRY003


def _find_public_keys() -> list[Path]:
    home = Path.home().absolute() / ".ssh"

    key_files = []

    for file in home.iterdir():
        try:
            if file.is_dir():
                continue

            with file.open(encoding="utf-8", mode="r") as f:
                data = f.read()

            if data.startswith("ssh-"):
                key_files.append(file)
        except PermissionError:
            continue

    log.debug(f"Found keys: {key_files}")
    return key_files


def copy_id(host: str, username: str | None, port: int | None, id_path: str | None) -> None:
    log.debug(f"copy_id")
    ssh = SSH(hostname=host, username=username, port=port)

    key_files = _find_public_keys() if not id_path else [_find_id(_resolve_path(id_path))]

    new_keys = []
    for key_file in key_files:
        log.debug(f"{key_file}")
        with open(key_file, encoding="utf-8") as f:
            data = f.read()
        new_keys.append(data.strip("\n"))

    log.debug(f"New keys:\n{_list_to_pretty(new_keys)}")

    if not ssh.check_exist_dir("~/.ssh"):
        log.debug("Dir .ssh doesn't exist")
        if os.environ.get("SSH_COPY_ID__DRY_RUN"):
            return

        ssh.run(f'mkdir "{ssh.resolve_path('~/.ssh')}"')

    if ssh.check_exist_file("~/.ssh/authorized_keys"):
        with ssh.sftp.open(f"{ssh.home}/.ssh/authorized_keys", "r") as f:
            authorized_keys = f.read().decode("utf-8")
    else:
        authorized_keys = ""

    exists_keys = [key for key in authorized_keys.split("\n") if len(key) > 0]
    log.debug(f"Exist keys:\n{_list_to_pretty(exists_keys)}")

    if len(exists_keys) == 0:
        log.debug("Exists keys not found")

    new_keys = [key for key in new_keys if key not in exists_keys]

    log.debug(f"New keys will be added: {len(new_keys)}")

    new_authorized_keys = "\n".join([*exists_keys, *new_keys])
    log.debug(f"Result keys:\n{_list_to_pretty([*exists_keys, *new_keys])}")

    if os.environ.get("SSH_COPY_ID__DRY_RUN"):
        return

    with ssh.sftp.open(f"{ssh.home}/.ssh/authorized_keys", "w") as f:
        f.write(new_authorized_keys.encode("utf-8"))

    print("Success.")

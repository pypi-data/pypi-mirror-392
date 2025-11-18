# ssh-copy-id-windows

---

ssh-copy-id for Windows OS.

https://github.com/overgodofchaos/ssh-copy-id-windows

# Install

---

### With PyPi:
```shell
pip (or pipx) install ssh-copy-id-windows
```

### Manual:
1. Download zip archive from [releases](https://github.com/overgodofchaos/ssh-copy-id-windows/releases).
2. Unzip the archive to any directory.
3. Install with `bat scripts` or manually add `bin` directory to `PATH`.



# Usage

---

```text
Usage: ssh-copy-id [OPTIONS] HOST

Arguments:
  HOST  Host name in format name@host or hostname from ssh config.
        \[required]

Options:
  -i, --id-file TEXT  Name or path of id key file. By default copy all keys
                      from ~/.ssh directory.
  -p, --port INTEGER  Host port
  --help              Show this message and exit.
```

# Examples

---

```shell
ssh-copy-id root@123.234.23.134
````

```shell
ssh-copy-id -i id_rsa.pub -p 1022 root@123.234.23.134
```
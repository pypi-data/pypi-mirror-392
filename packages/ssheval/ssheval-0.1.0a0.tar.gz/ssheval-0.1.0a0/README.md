# `ssheval`

A cross-platform pure Python script for executing remote commands over SSH and streaming raw stdout/stderr.

## 🚀 Features

- **Works on NT & POSIX:** Requires only Python 2+ and [`paramiko`](https://www.paramiko.org/) - no OpenSSH or PuTTY needed.
- **No manual password entry:** Provide credentials via command-line arguments for automation or scripting.
- **Faithfully streams stdout & stderr:** Outputs both streams in real time, preserving all bytes (works for text and binary data!).
- **Remote exit codes:** Exits with the same code as the remote command.
- **SSH-like stdin behavior:**  
  - Pipes stdin from your console or parent process **only if** input is provided (matches `ssh` behavior).
  - If nothing is piped, remote stdin is closed immediately.

## ⚡️ Why use this instead of plain ssh?

- **No SSH client required on Windows:** Works even where ssh is missing (ex: vanilla Windows).
- **Great for automation:** Integrates seamlessly with scripts and tools that need to provide credentials non-interactively.
- **Binary-safe:** Most SSH client wrappers mishandle binary data or don't stream both stdout and stderr in real time.
- **Stdin-pipes like ssh:** Remote command's stdin is hooked up only when data is piped in - just like the real `ssh`.

## 🛠️ Installation

```sh
pip install ssheval
```

[paramiko](https://pypi.org/project/paramiko/) required.


## 💻 Usage

Basic example:

```sh
python -m ssheval \
  --host example.com \
  --user youruser \
  --password 'yourpassword' \
  --command 'ls -lh /tmp'
```

Pipe something into the remote process:
```sh
echo "Hello remote world!" | python -m ssheval --host foo --user bar --password baz --command 'cat -'
```

Download a remote file (binary-safe):
```sh
python -m ssheval --host foo --user bar --password baz --command 'cat /usr/bin/ls' > local_ls_copy
```

### Arguments

| Argument     | Description                                |
|--------------|--------------------------------------------|
| `--host`     | Hostname or IP of the remote server        |
| `--user`     | SSH username                               |
| `--password` | SSH password (as a command line argument!) |
| `--port`     | SSH port (default: 22)                     |
| `--command`  | The remote command to execute              |


## 🔄 Stdin Handling

This script **matches SSH's behavior**:

- **If you pipe input in**, local stdin is streamed to the remote command.
- **If not**, remote stdin is immediately closed - remote commands like `cat` will finish (not hang).

**Examples:**

```sh
python -m ssheval ... --command 'cat -'         # stdin closed immediately
echo foo | python -m ssheval ... --command 'cat -'   # 'foo' is sent
```

## ⚠️ Limitations

- SSH key authentication not included (password-only; see `paramiko` docs for keys).
- No PTY/interactive shell allocation.
- Basic error handling and no advanced SSH features (X11, port forwarding).

## 🛠️ Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from __future__ import print_function

import argparse
import sys
import threading

import paramiko

if sys.version_info < (3,):
    sys_stdin_buffer = sys.stdin
    sys_stdout_buffer = sys.stdout
    sys_stderr_buffer = sys.stderr
else:
    sys_stdin_buffer = sys.stdin.buffer
    sys_stdout_buffer = sys.stdout.buffer
    sys_stderr_buffer = sys.stderr.buffer


def stream_pipe(src, dst, close_dst=False):
    try:
        while True:
            data = src.read(1)
            if not data:
                break
            dst.write(data)
            dst.flush()
    except Exception:
        pass  # Optionally log thread errors
    finally:
        if close_dst:
            try:
                dst.close()
            except Exception:
                pass


if sys.version_info < (2, 6):
    def set_daemon(thread):
        thread.setDaemon()
else:
    def set_daemon(thread):
        thread.daemon = True


def main():
    parser = argparse.ArgumentParser(description="Run a remote SSH command and output raw bytes to stdout/stderr.")
    parser.add_argument('--host', required=True, help='Remote host to connect to')
    parser.add_argument('--user', required=True, help='Username for SSH')
    parser.add_argument('--password', required=True, help='Password for SSH (if not using PEM key)')
    parser.add_argument('--port', type=int, default=22, help='SSH port (default: 22)')
    parser.add_argument('--command', required=True, help='Command to execute on remote host')
    args = parser.parse_args()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(args.host, port=args.port, username=args.user, password=args.password)
        stdin, stdout, stderr = client.exec_command(args.command)

        threads = []

        # Stream stdout and stderr in real time
        threads.append(threading.Thread(target=stream_pipe, args=(stdout, sys_stdout_buffer)))
        threads.append(threading.Thread(target=stream_pipe, args=(stderr, sys_stderr_buffer)))

        # Only pipe stdin if local stdin is not a tty (i.e., something is piped in)
        if not sys.stdin.isatty():
            threads.append(threading.Thread(target=stream_pipe, args=(sys_stdin_buffer, stdin, True)))

        for thread in threads:
            set_daemon(thread)
            thread.start()

        # Wait for remote command to exit
        exit_status = stdout.channel.recv_exit_status()

        for thread in threads:
            thread.join()

        sys.exit(exit_status)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()

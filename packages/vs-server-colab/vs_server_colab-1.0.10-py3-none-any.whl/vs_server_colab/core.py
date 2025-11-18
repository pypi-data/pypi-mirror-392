import os
import random
import subprocess
import socket
from pathlib import Path
from typing import Optional
from time import time
import re

def run_command(cmd: str, check: bool = True, capture_output: bool = True, text: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command synchronously and return CompletedProcess.

    Uses /bin/bash for consistent behavior with pipelines and shell features.
    """
    # Run with binary output to avoid UnicodeDecodeError on non-UTF8 bytes.
    raw = subprocess.run(cmd, shell=True, executable="/bin/bash", check=False,
                         capture_output=capture_output, text=False)
    if text:
        # Decode using 'replace' to avoid exceptions on invalid sequences.
        stdout = raw.stdout.decode('utf-8', errors='replace') if raw.stdout is not None else None
        stderr = raw.stderr.decode('utf-8', errors='replace') if raw.stderr is not None else None
        result = subprocess.CompletedProcess(raw.args, raw.returncode, stdout, stderr)
    else:
        result = raw

    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd,
                                            output=result.stdout, stderr=result.stderr)
    return result


def run_background_command(cmd: str, stdout_log: Optional[str] = None, stderr_log: Optional[str] = None) -> subprocess.Popen:
    """Start a command in background, optionally redirecting stdout/stderr to files.

    Returns a Popen object.
    """
    stdout = open(stdout_log, "a") if stdout_log else subprocess.DEVNULL
    stderr = open(stderr_log, "a") if stderr_log else subprocess.DEVNULL
    proc = subprocess.Popen(cmd, shell=True, executable="/bin/bash",
                            stdout=stdout, stderr=stderr, preexec_fn=os.setpgrp)
    return proc


def run_script_file(script_path: str, check: bool = True) -> subprocess.CompletedProcess:
    script = Path(script_path)
    if not script.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    try:
        script.chmod(script.stat().st_mode | 0o111)
    except Exception:
        pass
    return run_command(f"bash {str(script)}", check=check)


class VSExpose:
    """Main helper to install, start and teardown a code-server + ngrok setup."""

    def __init__(self):
        self.name = "VSCode Server Expose"
        self.description = "Sets up a VSCode server and exposes it via ngrok."
        self.author = "Hasinthaka"
        self.version = "1.0.0"
        self.repo = "https://github.com/hasinthaka/vs-server-script"
        self._path = os.path.dirname(os.path.abspath(__file__))

    def setup(self):
        print("Setting up VSCode server and ngrok...")
        for step in self._installation_steps():
            print(f"Executing: {step['title']} -> {step['file']}")
            script_file = os.path.join(self._path, step['file'])
            result = run_script_file(script_file)
            print(result.stdout or "(no stdout)")
            if result.stderr:
                print("script stderr:", result.stderr)
        print("Setup complete.")

    def start(self, auth_token: Optional[str] = None, silent: bool = False, log_file: str = 'vscolab.log'):
        port = self._get_random_port()
        print(f"Chosen port: {port}")
        self._start_vscode(port=port, log_file=log_file)
        self._start_ngrok(auth_token=auth_token, port=port, log_file='ngrok.log', silent=silent)
        print("VSCode server is running and exposed via ngrok.")

    def teardown(self):
        print("Tearing down VSCode server and ngrok...")
        for command in self._uninstallation_steps():
            print(f"Executing: {command}")
            result = run_command(command, check=False)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
        print("Teardown complete.")

    def _is_port_free(self, port: int) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", port))
            s.close()
            return True
        except OSError:
            return False

    def _get_random_port(self) -> int:
        for _ in range(50):
            port = random.randint(2000, 9000)
            if self._is_port_free(port):
                return port
        s = socket.socket()
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def _start_vscode(self, port: int = 8080, log_file: str = 'vscolab.log'):
        print("Starting VSCode server...")
        cmd = f"nohup code-server --port {port} > {log_file} 2>&1 &"
        proc = run_background_command(cmd, stdout_log=log_file, stderr_log=log_file)
        print(f"VSCode server started (pid={proc.pid}), logs -> {log_file}")

    def _start_ngrok(self, auth_token: Optional[str] = None, port: int = 8080, log_file: str = 'ngrok.log', silent: bool = False):
        print("Starting ngrok tunnel...")
        if auth_token:
            print("Configuring ngrok auth token...")
            run_command(f"ngrok authtoken {auth_token}")
        if not silent:
            cmd = f"nohup ngrok http {port} > {log_file} 2>&1 &"
            run_command(cmd)
            t = time()
            while True:
                result = run_command("curl --silent http://localhost:4040/api/tunnels", check=False)
                if result.returncode == 0 and '"public_url":"' in result.stdout:
                    server_url_match = re.search(r'"public_url":"(https://[^\"]+)"', result.stdout)
                    config_file = "/root/.config/code-server/config.yaml"
                    config = open(config_file).read() if os.path.exists(config_file) else ""
                    password = re.search(r'password:\s*(\S+)', config)
                    if server_url_match:
                        server_url = server_url_match.group(1)
                        print("ngrok tunnel established.")
                        print(f" - Your VSCode server is available at: {server_url}")
                        if password:
                            print(f" - Access password: {password.group(1)}")
                        print(f" - Logs available at: {log_file}")
                        break
                if time() - t > 15:
                    print("Timeout waiting for ngrok tunnel.")
                    break 

        else:
            cmd = f"ngrok http {port} --log=stdout &"
            run_command(cmd)

    def _installation_steps(self):
        return [
            {'title': "Install VSCode Server", 'file': "src/vs_server.sh"},
            {'title': "Install ngrok", 'file': "src/ngrok.sh"}
        ]

    def _uninstallation_steps(self):
        return [
            "rm -rf /usr/lib/code-server",
            "rm -rf /usr/local/bin/code-server",
            "rm -rf /usr/local/bin/ngrok"
        ]

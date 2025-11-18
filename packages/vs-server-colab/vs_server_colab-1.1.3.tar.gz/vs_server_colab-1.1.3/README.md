# VS Server Colab

![VSCode](https://img.shields.io/badge/VSCode-Visual%20Studio%20Code-007ACC?logo=visualstudiocode&logoColor=white) ![Colab](https://img.shields.io/badge/Colab-Google%20Colab-F9AB00?logo=googlecolab&logoColor=white) ![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)

VS Server Colab provides a lightweight workflow to run a headless VS Code (code-server) inside environments such as Google Colab and expose it securely via ngrok. It streamlines installation, launching, and teardown so you can use Colab like a remote VS Code instance.

## Key features

- Run VS Code (code-server) in cloud environments such as Colab.
- Expose the server securely with ngrok and support for auth tokens.
- Simple commands for install/setup, start, and teardown.
- Logs written to files for debugging and long-running sessions.

## Prerequisites

- Python 3.6+ (for package installation and CLI).
- A working internet connection.
- A free or paid ngrok account (recommended) if you want persistent tunnels. Create an account at https://ngrok.com and add your auth token.

## Quickstart

1. Install the package from PyPI:

```bash
pip install vs-server-colab
```

2. Configure ngrok (obtain your auth token at https://dashboard.ngrok.com/get-started/your-authtoken).

3. Run the setup (this runs the bundled install scripts in `src/`):

```bash
# setup (runs install scripts under src/)
vscolab setup
```

4. Start the server (a free port will be chosen automatically; provide your ngrok auth token):

```bash
vscolab start --auth-token YOUR_NGROK_TOKEN
```

5. When finished, teardown and remove installed artifacts:

```bash
vscolab teardown
```

## Usage examples and flags

- `vscolab setup` — Run the installation scripts for code-server and ngrok.
- `vscolab start --auth-token <TOKEN>` — Start code-server and ngrok tunnel (writes logs to `vscolab.log` and `ngrok.log`).
- `vscolab start --silent` — Start ngrok in silent background mode.
- `vscolab teardown` — Remove installed binaries and perform cleanup.

## Notes and best practices

- The package tries to pick an available port automatically. If you need a specific port, modify the code or start the server manually.
- Logs are written to `vscolab.log` (code-server) and `ngrok.log` by default. Inspect these when troubleshooting.
- Teardown currently removes installed binaries; it does not forcibly kill running processes by PID. If you need safer cleanup, consider adding PID files or system service integration.

## Contributing

Contributions, issues and feature requests are welcome. Please open a GitHub issue or submit a pull request.

## Connect

LinkedIn: [Hasinthaka Piyumal](https://www.linkedin.com/in/hasinthaka-piyumal)

## License

This project is licensed under the MIT License.

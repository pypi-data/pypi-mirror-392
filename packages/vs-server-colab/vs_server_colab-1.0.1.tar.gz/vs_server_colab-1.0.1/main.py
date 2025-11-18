"""Launcher script delegating to the packaged CLI.

This file remains at the project root for backwards compatibility when
running `python main.py`, but the actual implementation lives in
`vs_server_script` package.
"""

from vs_colab.cli import main


if __name__ == '__main__':
    main()
import argparse
from .core import VSExpose


def _build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="VSCode server expose helper")
    p.add_argument('action', choices=['setup', 'start', 'teardown'], help='Action to perform')
    p.add_argument('--auth-token', '-a', help='ngrok auth token', default=None)
    p.add_argument('--silent', '-s', action='store_true', help='Run ngrok silently')
    p.add_argument('--log', '-l', default='vscolab.log', help='VSCode server log file')
    return p


def main(argv=None):
    parser = _build_cli()
    args = parser.parse_args(argv)
    vs = VSExpose()
    if args.action == 'setup':
        vs.setup()
    elif args.action == 'start':
        vs.start(auth_token=args.auth_token, silent=args.silent, log_file=args.log)
    elif args.action == 'teardown':
        vs.teardown()


if __name__ == '__main__':
    main()

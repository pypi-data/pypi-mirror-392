from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os
import socket
import argparse
import signal
import sys
import pathlib
import warnings
import logging
import warnings

warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    module="pyftpdlib.authorizers"
)


def color_text(text: str, color: str) -> str:
    colors = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "gray": "\033[90m",
        "reset": "\033[0m"
    }
    color_code = colors.get(color.lower(), colors["reset"])
    return f"{color_code}{text}{colors['reset']}"


def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def enable_quiet_mode(handler, server):
    """Disable ALL terminal output, warnings, and logs."""

    # Suppress Python warnings
    warnings.filterwarnings("ignore")

    # Disable ALL logging everywhere
    logging.getLogger("pyftpdlib").setLevel(logging.CRITICAL)
    logging.getLogger().setLevel(logging.CRITICAL)
    logging.disable(logging.CRITICAL)

    # Disable handler logs
    handler.log_prefix = ""
    handler.log = lambda *a, **k: None

    # Disable server logs
    server.log = lambda *a, **k: None


def start_ftp_server(
    port=2121,
    username="batman",
    password="88888888",
    shared_folder=None,
    quiet=False,
    no_auth=False
):
    if shared_folder is None:
        shared_folder = os.path.join(
            os.path.dirname(__file__),
            "data", "ftp",
            pathlib.Path("DLE FSD BDA")
        )

    os.makedirs(shared_folder, exist_ok=True)

    # Configure authorizer
    authorizer = DummyAuthorizer()
    if no_auth:
        authorizer.add_anonymous(shared_folder, perm="elradfmwMT")
    else:
        authorizer.add_user(username, password, shared_folder, perm="elradfmwMT")

    # Handler setup
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.use_sendfile = False
    handler.timeout = 300
    handler.banner = "Python FTP Server Ready"
    handler.passive_ports = range(60000, 60100)

    host = get_ip_address()
    server = FTPServer((host, port), handler)

    # Enable completely silent mode
    if quiet:
        enable_quiet_mode(handler, server)

    # Ctrl+C handler
    def signal_handler(sig, frame):
        server.close_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Normal mode printing
    if not quiet:
        print("=" * 50)
        print("PYTHON FTP SERVER STARTED!")
        print("=" * 50)
        print(f"Server IP: {host}")
        print(f"FTP Port: {port}")
        print(f"Shared Folder: {shared_folder}")

        if no_auth:
            print("Authentication: DISABLED (Anonymous FTP)")
        else:
            print("Login Credentials:")
            print(f"   Username: {username}")
            print(f"   Password: {password}")

        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)

    # Run the server
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return
    except Exception:
        if not quiet:
            print("Server stopped or error occurred.")


def server():
    try:
        parser = argparse.ArgumentParser(description="Python FTP Server")

        parser.add_argument("-p", "--port", type=int, default=2121,
                            help="FTP server port")
        parser.add_argument("-u", "--username", default="batman",
                            help="FTP username")
        parser.add_argument("-P", "--password", default="88888888",
                            help="FTP password")
        parser.add_argument("-d", "--directory",
                            help="Shared folder path")
        parser.add_argument("-q", "--quiet", action="store_true",
                            help="Silent mode (no output)")
        parser.add_argument("--no-auth", action="store_true",
                            help="Enable anonymous login (disable authentication)")

        args = parser.parse_args()

        host = get_ip_address()
        print(f"FTP server running at {color_text(f'ftp://{host}:2121', 'blue')}")
        start_ftp_server(
            port=args.port,
            username=args.username,
            password=args.password,
            shared_folder=args.directory,
            quiet=True,
            no_auth=True
        )

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    server()

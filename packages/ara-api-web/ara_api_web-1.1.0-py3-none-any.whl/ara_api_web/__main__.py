from email.policy import default

import click

from ara_api_web._core.server import run_server


@click.command
@click.option(
    "--host",
    default="0.0.0.0",
    help="Адрес хоста для сервера",
    show_default=True,
)
@click.option(
    "--port",
    default=8080,
    help="Порт для сервера",
    show_default=True,
)
def main(host: str, port: int):
    run_server(host=host, port=port)


if __name__ == "__main__":
    main()

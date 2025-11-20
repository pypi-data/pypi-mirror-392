from importlib.metadata import version
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class UI:
    def __init__(self) -> None:
        self.console = Console()

        try:
            self._api_version = version("ara_api_web")
        except Exception:
            self._api_version = "1.1.0"  # ! HARD VERSION

    def _create_logo(self) -> Text:
        logo = """
                          ██████████
                  ███████████████  ███
             █████ ████    ██████   ██
            ████████    ██   ████████
         ███████    ████   ███   ███
     ████████   █████    ███
  ███████    ████    █████
              ███████
        """

        return Text(logo, style="bold cyan")

    def display_startup_banner(
        self,
        host: str,
        port: int,
        grpc_status: str = "connected",
        grpc_address: Optional[str] = None,
    ):
        self.console.clear()

        logo = self._create_logo()

        display_host = "localhost" if host == "0.0.0.0" else host
        server_url = f"http://{display_host}:{port}/"

        info_text = Text()
        info_text.append("\n")
        info_text.append("\n\nARA API WEB", style="bold cyan")
        info_text.append(f"\nv{self._api_version}\n", style="cyan")
        info_text.append("REST API Interface for ARA Drone\n", style="dim white")
        info_text.append(
            "Server started on: " + server_url, style="bold green underline"
        )

        layout_table: Table = Table.grid(padding=(0, 1))
        layout_table.add_column(width=40, justify="left")
        layout_table.add_column(width=1, style="dim cyan")
        layout_table.add_column(justify="left")
        layout_table.add_row(logo, "", info_text)

        main_panel = Panel(layout_table, border_style="cyan", padding=(1, 2))

        self.console.print(main_panel)
        self.console.print()

        # TODO: add logic for getting status of services
        # status_table = Table(
        #     show_header=True,
        #     header_style="bold cyan",
        #     show_edge=False,
        #     pad_edge=False,
        # )

        # status_table.add_column("Service", style="bold magenta", width=20)
        # status_table.add_column("Address", style="white", width=30)
        # status_table.add_column("Status", style="yellow", width=20)

        # status_table.add_row(
        #     "REST API",
        #     f"http://{host}:{port}",
        #     "[bold green]Running[/bold green]",
        # )

        # status_table.add_row(
        #     "Swagger UI",
        #     f"http://{host}:{port}/docs",
        #     "[bold green]Available[/bold green]",
        # )

        # if grpc_status == "connected":
        #     grpc_display = grpc_address or "localhost:50051"
        #     status_table.add_row(
        #         "gRPC Backend",
        #         grpc_display,
        #         "[bold green]Connected[/bold green]",
        #     )
        # elif grpc_status == "error":
        #     status_table.add_row(
        #         "gRPC Backend",
        #         "N/A",
        #         "[bold red]Error[/bold red]",
        #     )
        # else:
        #     status_table.add_row(
        #         "gRPC Backend",
        #         "N/A",
        #         "[bold yellow]Disconnected[/bold yellow]",
        #     )

        # status_panel = Panel(
        #     status_table,
        #     title="[bold cyan]Services Status[/bold cyan]",
        #     border_style="cyan",
        #     padding=(1, 2),
        # )

        # self.console.print(status_panel)
        # self.console.print()

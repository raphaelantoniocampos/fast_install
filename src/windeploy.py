import argparse
import json
import subprocess
from time import sleep

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from rich.panel import Panel

import builder

INQUIRER_KEYBINDINGS = {
    "answer": [
        {"key": "enter"},
    ],
    "interrupt": [
        {"key": "c-c"},
        {"key": "escape"},
    ],
    "down": [
        {"key": "down"},
        {"key": "j"},
    ],
    "up": [
        {"key": "up"},
        {"key": "k"},
    ],
    "toggle": [
        {"key": "space"},
    ],
    "toggle-all-true": [
        {"key": "a"},
    ],
}


class PackageManager:
    """
    Represents a package manager with its name, cli install cmd, and powershell install script.
    """

    def __init__(self, name: str, cli_install: list[str], script: str):
        self.name = name
        self.cli_install = cli_install
        self.script = script

    def is_installed(self) -> bool:
        """
        Checks if a package manager is installed.
        Returns:
            bool: True if installed, False otherwise.
        """
        try:
            result = subprocess.run(
                f"{self.cli_install[0]} --version",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                check=False,
            )
            if result.returncode == 0:
                return True
        except Exception:
            return False

    def install(self):
        """
        Installs the Package Manager using the powerShell script.
        """
        console.print(f"[bold yellow]Instalando {self.name}...[/bold yellow]")
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-InputFormat",
                "None",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                self.script,
            ],
            shell=True,
        )
        if self.name == "Winget":
            subprocess.run(
                ["winget", "source", "update", "--accept-source-agreements"],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        console.print(f"[green]{self.name} instalado com sucesso![/green]")


CHOCOLATEY = PackageManager(
    name="Chocolatey",
    cli_install=["choco", "install", "-y"],
    script=(
        "[System.Net.ServicePointManager]::SecurityProtocol = 3072; "
        "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    ),
)
SCOOP = PackageManager(
    name="Scoop",
    cli_install=["scoop", "install", "-y"],
    script=(
        "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser;"
        "Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression"
    ),
)
WINGET = PackageManager(
    name="Winget",
    cli_install=[
        "winget",
        "install",
        "--silent",
        "--accept-package-agreements",
        "--accept-source-agreements",
        "--scope",
        "machine",
    ],
    script="irm https://github.com/asheroto/winget-install/releases/latest/download/winget-install.ps1 | iex",
)


class App:
    """
    Represents a app with its package manager, name, package name and install method.
    """

    def __init__(self, name: str, package_name: list[str], package_manager: str):
        self.name = name
        self.package_name = package_name
        self.package_manager = self._get_package_manager(package_manager)
        self.install_cmd = self.package_manager.cli_install + [*package_name]
        self.is_installed = False

    def _get_package_manager(self, package_manager_name: str) -> PackageManager:
        match package_manager_name:
            case "Chocolatey":
                return CHOCOLATEY
            case "Scoop":
                return SCOOP
            case "Winget":
                return WINGET

    def install(self):
        console.print(f"[bold cyan]Instalando {self.name}...[/bold cyan]")
        subprocess.run(
            self.install_cmd,
            shell=True,
        )
        console.print(f"[bold green]{self.name} instalado com sucesso![/bold green]")


def check_package_managers(selected_apps) -> list[PackageManager]:
    """
    Return missing package managers.
    """
    package_managers = []
    for app in selected_apps:
        if not app.package_manager.is_installed():
            console.print(
                f"O programa {app.name} necessita de [cyan]{app.package_manager.name}[/] para ser instalado."
            )
            package_managers.append(app.package_manager)
    return package_managers


def install_apps(selected_apps) -> None:
    """
    Installs the selected apps.

    Args:
        selected_apps (list): A list of apps selected by the user.
    """
    for app in selected_apps:
        app.install()


def auto_mode():
    """Automated execution mode"""
    try:
        print("Instalando pacotes...")
        for app in APPS:
            if not app.is_installed:
                app.install()

        print("Atualizando pacotes...")
        subprocess.run(
            [
                "winget",
                "upgrade",
                "--all",
                "--silent",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ],
            check=True,
        )

    except Exception as e:
        print(f"Erro no modo automático: {str(e)}")
        return 1

    return 0


def interactive_mode():
    """Interactive execution mode"""
    installed = sum(1 for app in APPS if app.is_installed)
    choices = [
        *[app.name for app in APPS if not app.is_installed],
        Separator(),
        *[
            Choice(app.name, name=app.name, enabled=True)
            for app in APPS
            if app.is_installed
        ],
    ]

    console.print(
        Panel.fit(
            "[bold cyan]WinDeploy[/bold cyan] - [yellow]Ferramenta Automática de Pacotes Windows[/yellow]",
            subtitle="[green]github.com/raphaelantoniocampos/windeploy[/green]",
        )
    )

    console.print("")
    console.print(
        Panel.fit(
            f"[green]✓[/green] {installed} apps instalados\n"
            f"[red]✗[/red] {len(APPS) - installed} apps disponíveis",
            title="[bold]Status do Sistema[/bold]",
        )
    )
    console.print("")
    selected_names = inquirer.checkbox(
        message="Selecione os programas que deseja instalar ou atualizar:",
        choices=choices,
        keybindings=INQUIRER_KEYBINDINGS,
        mandatory=False,
        instruction="Use as teclas de direção para navegar",
        long_instruction="[Espaço] seleciona • [Enter] confirma • [Esc] cancela\nMIT License • © 2025 Raphael Campos",
    ).execute()

    if selected_names:
        selected_apps = [app for app in APPS if app.name in selected_names]
        proceed = inquirer.confirm(message="Continuar?", default=True).execute()

        if proceed:
            package_managers_to_install = check_package_managers(selected_apps)
            if package_managers_to_install:
                for package_manager in package_managers_to_install:
                    package_manager.install()
                    console.print("[yellow]Por favor, reinicie o programa.[/]")
                    input("\nPressione Enter para sair...")
                    return
            install_apps(selected_apps)
        else:
            console.print("[bold yellow]Operação cancelada![/bold yellow]")
    else:
        console.print("[bold yellow]Nenhum programa foi selecionado![/bold yellow]")
    input("\nPressione Enter para sair...")
    return 0


def load_apps_from_json(json_file) -> list[App]:
    """
    Load apps from a JSON file.

    Args:
        json_file (str): Path to the JSON file.

    Returns:
        list: A list of App objects.
    """
    with open(json_file, "r") as file:
        apps_data = json.load(file)

    installed_packages = subprocess.check_output(
        ["winget", "list", "--accept-source-agreements"],
        text=True,
        stderr=subprocess.DEVNULL,
    ).lower()

    apps = []
    for app_data in apps_data:
        app = App(**app_data)
        app.is_installed = any(
            pkg.lower() in installed_packages for pkg in app.package_name
        )
        apps.append(app)

    return apps


def main(json_file):
    """Main function"""
    global APPS
    try:
        if not WINGET.is_installed():
            WINGET.install()

        APPS = load_apps_from_json(json_file)

        if ARGS.auto:
            auto_mode()
        else:
            interactive_mode()

    except json.decoder.JSONDecodeError as e:
        sleep(1)
        console.print(e)
        console.print(
            "\n[yellow]Arquivo JSON vazio.[/]\nLeia o [cyan]README.md[/] para mais informações."
        )
        return 1
    except KeyboardInterrupt:
        sleep(1)
        console.print("\n[yellow]Interrompido pelo usuário.[/]\n")
        input("\nPressione Enter para sair...")
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WinDeploy")
    parser.add_argument(
        "json_path",
        type=str,
        help="Caminho para o arquivo JSON contendo a lista de aplicativos.",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Executar em modo automatizado sem interface",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Gerar executável",
    )
    ARGS = parser.parse_args()

    if ARGS.build:
        builder.build(json_path=ARGS.json_path, auto=ARGS.auto)
        exit(0)

    console = Console()
    exit_code = main(ARGS.json_path)
    exit(exit_code)

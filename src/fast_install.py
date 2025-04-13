import argparse
import json
import os
import subprocess
from time import sleep

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel

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
                check=False
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
        console.print(f"[green]{self.name} instalado com sucesso![/green]")


class App:
    """
    Represents a app with its package manager, name, package name and install method.
    """

    def __init__(self, name: str, package_name: list[str], package_manager: str):
        self.name = name
        self.package_name = package_name
        self.package_manager = self._get_package_manager(package_manager)
        self.install_cmd = self.package_manager.cli_install + [*package_name]

    def _get_package_manager(self, package_manager_name: str) -> PackageManager:
        match package_manager_name:
            case "Chocolatey":
                return PackageManager(
                    name="Chocolatey",
                    cli_install=["choco" ,"install", "-y"],
                    script=(
                        "[System.Net.ServicePointManager]::SecurityProtocol = 3072; "
                        "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
                    ),
                )
            case "Scoop":
                return PackageManager(
                    name="Scoop",
                    cli_install=["scoop", "install", "-y"],
                    script=(
                        "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser;"
                        "Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression"
                    ),
                )
            case "Winget":
                return PackageManager(
                    name="Winget", 
                    cli_install=["winget", "install", "-e", "--accept-package-agreements"],
                    script="irm https://github.com/asheroto/winget-install/releases/latest/download/winget-install.ps1 | iex",
                )

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
            console.print(f"O programa {app.name} necessita de [cyan]{app.package_manager.name}[/] para ser instalado.")
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
    return [App(**app) for app in apps_data]


def main(json_file):
    """
    Main function to:
    - Display a menu for program selection, install selected programs and its package managers if needed.
    """
    global APPS
    try:
        APPS = load_apps_from_json(json_file)
        console.print(
            Panel.fit("[bold green]Menu de Instalação de Programas[/bold green]")
        )

        selected_names = inquirer.checkbox(
            message="Selecione os programas que deseja instalar:",
            choices=[app.name for app in APPS],
            keybindings=INQUIRER_KEYBINDINGS,
            mandatory=False,
            instruction="[Enter] para continuar",
            long_instruction="Use as [setas] do teclado para navegar\n[Espaço] para selecionar os aplicativos\n[Esc] ou [Ctrl+C] para sair."
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
                        return
                install_apps(selected_apps)
            else:
                console.print("[bold yellow]Operação cancelada![/bold yellow]")
        else:
            console.print("[bold yellow]Nenhum programa foi selecionado![/bold yellow]")

    except json.decoder.JSONDecodeError as e:
        sleep(1)
        console.print(e)
        console.print(
            "\n[yellow]Arquivo JSON vazio.[/]\nLeia o [cyan]README.md[/] para mais informações."
        )
        return
    except KeyboardInterrupt:
        sleep(1)
        console.print(
            "\n[yellow]Interrompido pelo usuário.[/]\n"
        )
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fast Install")
    parser.add_argument(
        "json_file",
        type=str,
        help="Caminho para o arquivo JSON contendo a lista de aplicativos.",
    )
    args = parser.parse_args()

    console = Console()
    main(args.json_file)
    input("\nPressione Enter para sair...")

import argparse
import json
import os
import subprocess
from dataclasses import dataclass
from time import sleep

from questionary import checkbox, confirm
from rich.console import Console
from rich.panel import Panel


@dataclass
class Dep:
    """
    Represents a dependency with its name, os path and PowerShell install script.
    """

    name: str
    path: str
    script: str


@dataclass
class App:
    """
    Represents a app with its name, package name script and optional params.
    """

    name: str
    pkg_name: str
    params: str | None


# Not using scoop for now
# SCOOP = Dep(
#     name="Scoop",
#     path=os.path.expanduser("~\\scoop"),
#     script=(
#         "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser;"
#         "Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression"
#     ),
# )

CHOCOLATEY = Dep(
    name="Chocolatey",
    path="C:\\ProgramData\\chocolatey",
    script=(
        "[System.Net.ServicePointManager]::SecurityProtocol = 3072; "
        "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    ),
)


def check_dep(dep: Dep) -> bool:
    """
    Checks if a dependency exists at the given path. If not, installs it using
    the provided PowerShell script.

    Args:
        dep (Dep): The dependency to check and potentially install.

    Returns:
        bool: Bool indicating if a restart is needed.
    """
    if not os.path.exists(dep.path):
        console.print(f"[bold yellow]Instalando {dep.name}...[/bold yellow]")
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-InputFormat",
                "None",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                dep.script,
            ],
            shell=True,
        )
        console.print(f"[green]{dep.name} instalado com sucesso![/green]")
        needs_restart = True
        return needs_restart
    else:
        console.print(f"[green]{dep.name} já está instalado![/green]")
        needs_restart = False
        return needs_restart


def install_apps(selected_apps):
    """
    Installs the selected programs using Chocolatey.

    Args:
        selected_apps (list): A list of apps selected by the user.
    """
    for app in selected_apps:
        params = app.params if app.params else ""
        console.print(f"[bold cyan]Instalando {app.name}...[/bold cyan]")
        subprocess.run(["choco", "install", "-y", app.pkg_name, params], shell=True)
        console.print(f"[bold green]{app.name} instalado com sucesso![/bold green]")


def load_apps_from_json(json_file):
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
    - Check and install dependencies (Scoop and Chocolatey).
    - Display a menu for program selection and install selected programs.
    """
    global APPS
    try:
        APPS = load_apps_from_json(json_file)

        console.print("[bold]Verificando dependências[/bold]")
        needs_restart = check_dep(CHOCOLATEY)
        if needs_restart:
            console.print("[yellow]Reinicie o programa![/yellow]")
            sleep(2)
            return

        console.print(
            Panel.fit("[bold green]Menu de Instalação de Programas[/bold green]")
        )
        selected_names = checkbox(
            "Selecione os programas que deseja instalar:\n",
            choices=[app.name for app in APPS],
        ).ask()

        if selected_names:
            selected_apps = [app for app in APPS if app.name in selected_names]
            if confirm("Deseja instalar os programas selecionados?").ask():
                install_apps(selected_apps)
            else:
                console.print("[bold yellow]Operação cancelada![/bold yellow]")
        else:
            console.print("[bold yellow]Nenhum programa foi selecionado![/bold yellow]")

    except Exception as e:
        sleep(1)
        console.print(e)
        console.print(
            "\n[yellow]Arquivo JSON vazio.[/]\nLeia o [cyan]README.md[/] para mais informações."
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

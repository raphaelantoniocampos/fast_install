import ctypes
import json
import os
import subprocess
import sys
from time import sleep

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel

# import builder

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


def is_run_as_admin():
    """Verifica se o script está sendo executado como admin"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def elevate_as_admin():
    """Solicita elevação de privilégios"""
    if not is_run_as_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


def check_domain_user():
    """Verifica se está sendo executado como usuário de domínio"""
    username = os.getenv("USERNAME", "")
    return "@" in username or "\\" in username


def ensure_admin_rights():
    """Garante que o script tenha privilégios administrativos"""
    if is_run_as_admin():
        return True

    params = {
        "lpVerb": "runas",
        "lpFile": sys.executable,
        "lpParameters": " ".join(sys.argv),
        "lpDirectory": os.path.dirname(sys.executable),
        "nShow": 1,  # SW_SHOWNORMAL
    }

    if check_domain_user():
        from ctypes import wintypes

        params["nShow"] = 5  # SW_SHOW
        params["fMask"] = 0x00000040  # SEE_MASK_NOCLOSEPROCESS

        # ShellExecuteEx fornece mais controle
        class SHELLEXECUTEINFOW(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("fMask", wintypes.ULONG),
                ("hwnd", wintypes.HWND),
                ("lpVerb", wintypes.LPCWSTR),
                ("lpFile", wintypes.LPCWSTR),
                ("lpParameters", wintypes.LPCWSTR),
                ("lpDirectory", wintypes.LPCWSTR),
                ("nShow", ctypes.c_int),
                ("hInstApp", wintypes.HINSTANCE),
                ("lpIDList", ctypes.c_void_p),
                ("lpClass", wintypes.LPCWSTR),
                ("hKeyClass", wintypes.HKEY),
                ("dwHotKey", wintypes.DWORD),
                ("hMonitor", wintypes.HANDLE),
                ("hProcess", wintypes.HANDLE),
            ]

        sei = SHELLEXECUTEINFOW()
        sei.cbSize = ctypes.sizeof(sei)
        sei.lpVerb = "runas"
        sei.lpFile = sys.executable
        sei.lpParameters = " ".join(sys.argv)
        sei.nShow = 5  # SW_SHOW

        if not ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei)):
            raise ctypes.WinError()

        sys.exit(0)
    else:
        # Comportamento padrão para usuários locais
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)


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
                check=False,
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

CUSTOM = PackageManager(
    name="Custom",
    cli_install=[],
    script="",
)


class Package:
    """
    Represents a package with its package manager, name, package name, install method and install status.
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
            case "Custom":
                return CUSTOM

    def install(self):
        console.print(f"[bold cyan]Instalando {self.name}...[/bold cyan]")
        subprocess.run(
            self.install_cmd,
            shell=True,
        )

        console.print(f"[bold green]{self.name} instalado com sucesso![/bold green]")


def check_package_managers(selected_packages) -> list[PackageManager]:
    """
    Return missing package managers.
    """
    package_managers = []
    for package in selected_packages:
        if (
            not package.package_manager.is_installed()
            and not package.package_manager.name == "Custom"
        ):
            console.print(
                f"O programa {package.name} necessita de [cyan]{
                    package.package_manager.name
                }[/] para ser instalado."
            )
            package_managers.append(package.package_manager)
    return package_managers


def install_packages(selected_packages) -> None:
    """
    Installs the selected packages.

    Args:
        selected_packages (list): A list of packages selected by the user.
    """
    for package in selected_packages:
        package.install()


def silent_mode():
    """Automated execution mode"""
    try:
        print("Instalando pacotes...")
        for package in PACKAGES:
            if not package.is_installed:
                package.install()

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
        print(f"Erro no modo silencioso: {str(e)}")
        return 1

    return 0


def interactive_mode():
    """Interactive execution mode"""
    installed = sum(1 for package in PACKAGES if package.is_installed)
    choices = [
        *[package.name for package in PACKAGES],
    ]

    console.print(
        Panel.fit(
            "[bold cyan]AutoPkg-Windows[/bold cyan] - [yellow]Ferramenta Automática de Pacotes Windows[/yellow]",
            subtitle="[green]github.com/raphaelantoniocampos/autopkg-windows[/green]",
        )
    )

    console.print("")
    console.print(
        Panel.fit(
            f"{installed} pacotes instalados\n"
            f"{len(PACKAGES) - installed} pacotes disponíveis",
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
        selected_packages = [
            package for package in PACKAGES if package.name in selected_names
        ]
        proceed = inquirer.confirm(message="Continuar?", default=True).execute()

        if proceed:
            package_managers_to_install = check_package_managers(selected_packages)
            if package_managers_to_install:
                for package_manager in package_managers_to_install:
                    package_manager.install()
                    console.print("[yellow]Por favor, reinicie o programa.[/]")
                    input("\nPressione Enter para sair...")
                    return
            install_packages(selected_packages)
        else:
            console.print("[bold yellow]Operação cancelada![/bold yellow]")
    else:
        console.print("[bold yellow]Nenhum programa foi selecionado![/bold yellow]")
    input("\nPressione Enter para sair...")
    return 0


def check_installed_packages(packages: list[Package]):
    installed_packages = subprocess.check_output(
        ["winget", "list", "--accept-source-agreements"],
        text=True,
        stderr=subprocess.DEVNULL,
    ).lower()

    for package in packages:
        package.is_installed = any(
            pkg.lower() in installed_packages for pkg in package.package_name
        )
        if package.name == "MarkText" and package.is_installed:
            set_marktext_default()
            remove_marktext_shortcut()
    return packages


def set_marktext_default():
    """Configura o MarkText como editor padrão para arquivos .md e .markdown"""
    marktext_path = os.path.join(os.environ["ProgramFiles"], "MarkText", "marktext.exe")
    file_types = [".md", ".md", ".markdown", ".markdown"]

    if not os.path.exists(marktext_path):
        print(f"MarkText não encontrado em {marktext_path}")
        return False

    for ext in file_types:
        try:
            subprocess.run(
                f'ftype MarkText{ext}="{marktext_path}" "%1"',
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            subprocess.run(
                f"assoc {ext}=MarkText{ext}",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            print(f"Associação {ext} configurada com sucesso para MarkText")
            return True

        except subprocess.CalledProcessError as e:
            print(
                f"Falha ao associar extensão {ext}:\nSaída: {
                    e.stdout.decode().strip()
                }\nErro: {e.stderr.decode().strip()}"
            )
    return False


def remove_marktext_shortcut():
    """Remove o atalho do MarkText da área de trabalho pública"""
    public_desktop = os.path.join(os.environ["PUBLIC"], "Desktop")
    shortcut_path = os.path.join(public_desktop, "MarkText.lnk")
    try:
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            console.print(
                "[green]Atalho do MarkText removido da área de trabalho pública[/green]"
            )
            return True
    except Exception as e:
        console.print(f"[red]Erro ao remover atalho: {str(e)}[/red]")
    return False


def verify_winget():
    if not WINGET.is_installed():
        WINGET.install()
        return

    subprocess.run(
        ["winget", "source", "reset", "--force"],
        shell=True,
        check=False,
    )


def load_packages_from_json(json_path):
    PACKAGES = [
        Package(name="Anydesk", package_name=['Anydesk'], package_manager="Winget"),
        Package(name="Google Chrome", package_name=['Google.Chrome'], package_manager="Winget"),
        Package(name="Driver Booster", package_name=['XPFG20V78LRMWG'], package_manager="Winget"),
        Package(name="Firefox", package_name=['Mozilla Firefox'], package_manager="Winget"),
        Package(name="Java", package_name=['Java 8'], package_manager="Winget"),
        Package(name="Winrar", package_name=['WinRAR'], package_manager="Winget"),
        Package(name="Foxit Reader", package_name=['Foxit.FoxitReader'], package_manager="Winget"),
        Package(name="Office 2019", package_name=['office2019proplus', '--params', "'/Language:pt-BR'"], package_manager="Chocolatey"),
        Package(name="Microsoft Office 365", package_name=['Microsoft.Office'], package_manager="Winget"),
        Package(name="Ativar Office", package_name=['powershell', '& ([ScriptBlock]::Create((irm https://get.activated.win)))', '/K-Office'], package_manager="Custom"),
        Package(name="Ativar Windows", package_name=['powershell', '& ([ScriptBlock]::Create((irm https://get.activated.win)))', '/K-Windows'], package_manager="Custom"),
        Package(name="Ativar Windows+Office", package_name=['powershell', '& ([ScriptBlock]::Create((irm https://get.activated.win)))', '/K-WindowsOffice'], package_manager="Custom"),
    ]

    return PACKAGES

def main():
    json_path = None
    """Main function"""
    os.chdir(os.path.expanduser("~"))
    global PACKAGES

    ensure_admin_rights()
    try:
        verify_winget()
        packages = load_packages_from_json(json_path)
        PACKAGES = check_installed_packages(packages)

        if ARGS.silent:
            silent_mode()
        else:
            interactive_mode()

    except json.decoder.JSONDecodeError as err:
        sleep(1)
        console.print(
            f"\n[yellow]Arquivo JSON com erro.[/]\n{
                err
            }\n\nLeia o [cyan]README.md[/] para mais informações."
        )
        return 1
    except KeyboardInterrupt:
        sleep(1)
        console.print("\n[yellow]Interrompido pelo usuário.[/]\n")
        input("\nPressione Enter para sair...")
        return 0


class Args:

    silent = False
    build = False

ARGS = Args()

    
if __name__ == "__main__":

    console = Console()
    main()
        
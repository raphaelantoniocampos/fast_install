import json
import subprocess
from pathlib import Path


def build(json_path: str, silent: bool, hide_console: bool = False):
    def rewrite_load_json(json_path, temp_f):
        with open(json_path, "r", encoding="utf-8") as file:
            packages_data = json.load(file)
            packages_list = """
    PACKAGES = [
"""
            for package in packages_data:
                packages_list += f'        Package(name="{
                    package["name"]
                }", package_name={package["package_name"]}, package_manager="{
                    package["package_manager"]
                }"),\n'
            packages_list += "    ]\n"

        temp_f.write("def load_packages_from_json(json_path):")
        temp_f.write(packages_list)
        temp_f.write("\n    return PACKAGES\n\n")
        temp_f.write("def main():\n")
        temp_f.write("    json_path = None\n")

    def rewrite_if_name_main(temp_f):
        temp_f.write("class Args:\n")
        temp_f.write(f"""
    silent = {str(silent)}
    build = False

ARGS = Args()\n
    """)
        temp_f.write("""
if __name__ == "__main__":\n
    console = Console()
    main()
        """)

    original_script = Path("./main.py")
    temp_script = Path("./temp.py")
    json_path = Path(json_path)

    with open(original_script, "r", encoding="utf-8") as original_f:
        original_lines = original_f.read().split("\n")
        with open(temp_script, "w", encoding="utf-8") as temp_f:
            ignore = False
            for line in original_lines:
                if "import builder" in line:
                    temp_f.write("# ")

                if line.startswith("def load"):
                    rewrite_load_json(json_path, temp_f)
                    ignore = True

                if '    """Main function"""' in line:
                    ignore = False

                if line.startswith('if __name__ == "__main__":'):
                    rewrite_if_name_main(temp_f)
                    ignore = True

                if not ignore:
                    temp_f.write(line)
                    temp_f.write("\n")

    subprocess.run(["uv", "run", "ruff", "check", "--fix", "temp.py"])
    ico_path = (
        "icos/autopkg-windows-green.ico"
        if not silent
        else "icos/autopkg-windows-blue.ico"
    )
    name = "autopkg-windows" if not silent else "autopkg-windows-silent"
    hide_console = "temp.py" if not hide_console else "--hide-console=hide-early"
    subprocess.run(
        [
            "uv",
            "run",
            "pyinstaller",
            "--onefile",
            f"--icon={ico_path}",
            f"-n={name}",
            hide_console,
            "temp.py",
        ]
    )
    temp_script.unlink()
    return 0

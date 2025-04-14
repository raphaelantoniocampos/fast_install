import subprocess
import argparse
import json
from pathlib import Path


def build(json_path: str):
    original_script = Path("src/windeploy.py")
    temp_script = Path("src/temp.py")
    json_file = Path(json_path)

    with open(original_script, "r", encoding="utf-8") as original_f:
        original_lines = original_f.read().split("\n")
        with open(temp_script, "w", encoding="utf-8") as temp_f:
            ignore = False
            for line in original_lines:
                if line.startswith("def load"):
                    rewrite_load_json(json_file, temp_f)
                    ignore = True

                if line.startswith("    global APPS"):
                    ignore = False

                if line.startswith('if __name__ == "__main__":'):
                    rewrite_if_name_main(temp_f)
                    ignore = True

                if not ignore:
                    temp_f.write(line)
                    temp_f.write("\n")

    subprocess.run(["uv", "run", "ruff", "check", "--fix", "src/temp.py"])
    subprocess.run(["uv", "run", "pyinstaller", "--onefile", "--icon=icos/windeploy.ico", "-n=windeploy", "src/temp.py"])
    temp_script.unlink()


def rewrite_load_json(json_file, temp_f):
    with open(json_file, "r", encoding="utf-8") as file:
        apps_data = json.load(file)
        apps_list = """
    APPS = [
"""
        for app in apps_data:
            apps_list += f'        App(name="{app["name"]}", package_name={app["package_name"]}, package_manager="{app["package_manager"]}"),\n'
        apps_list += "    ]\n"

    temp_f.write("def load_apps_from_json(json_file):")
    temp_f.write(apps_list)
    temp_f.write("\n    return APPS\n\n")
    temp_f.write("def main():\n")
    temp_f.write("    json_file = None\n")


def rewrite_if_name_main(temp_f):
    temp_f.write('if __name__ == "__main__":\n')
    temp_f.write("""
    console = Console()
    main()
    input("\\nPressione Enter para sair...")
    console = Console()
    """)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WinDeploy Builder")
    parser.add_argument(
        "json_path",
        type=str,
        help="Caminho para o arquivo JSON contendo a lista de aplicativos.",
    )
    args = parser.parse_args()

    build(args.json_path)

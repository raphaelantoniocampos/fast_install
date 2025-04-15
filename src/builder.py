import subprocess
import json
from pathlib import Path


def build(json_path: str, auto: bool):
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
        temp_f.write("""
    try:
        global APPS\n""")

    def rewrite_if_name_main(temp_f):
        temp_f.write("class Args:\n")
        temp_f.write(f"""
    auto = {str(auto)}
    build = False

ARGS = Args()\n
    """)
        temp_f.write("""
if __name__ == "__main__":\n
    console = Console()
    main()
        """)

    original_script = Path("./src/windeploy.py")
    temp_script = Path("./src/temp.py")
    json_file = Path(json_path)

    with open(original_script, "r", encoding="utf-8") as original_f:
        original_lines = original_f.read().split("\n")
        with open(temp_script, "w", encoding="utf-8") as temp_f:
            ignore = False
            for line in original_lines:
                if "import builder" in line:
                    temp_f.write("# ")

                if line.startswith("def load"):
                    rewrite_load_json(json_file, temp_f)
                    ignore = True

                if "if not WINGET.is_installed():" in line:
                    ignore = False

                if line.startswith('if __name__ == "__main__":'):
                    rewrite_if_name_main(temp_f)
                    ignore = True

                if not ignore:
                    temp_f.write(line)
                    temp_f.write("\n")

    subprocess.run(["uv", "run", "ruff", "check", "--fix", "src/temp.py"])
    ico_path = "icos/windeploy.ico" if not auto else "icos/windeploy_auto.ico"
    name = "windeploy" if not auto else "windeploy_auto"
    subprocess.run(
        [
            "uv",
            "run",
            "pyinstaller",
            "--onefile",
            f"--icon={ico_path}",
            f"-n={name}",
            "src/temp.py",
        ]
    )
    # temp_script.unlink()
    return 0

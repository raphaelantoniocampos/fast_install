# Fast Install

**Fast Install** is a command-line tool developed in Python to simplify the installation of programs and dependencies on Windows systems using the **Chocolatey** package manager. It allows you to quickly select and install a list of applications from a JSON file.
---

## Features

- **Automatic Dependency Management**:
  - Checks for and installs `Chocolatey` if it are not already installed.
- **Program Installation**:
  - Provides a menu to select programs for installation via Chocolatey.
  - Support for installing multiple applications at once.
  - Reads application lists from JSON files.

---

## Prerequisites 

### System
- **Windows** (PowerShell required)
- **Administrator Privileges** (needed to install dependencies and programs)
- **uv** (python package manager)
- **Python3.10 or higher**
- **Chocolatey** (will be installed automatically if not present).

---

## Usage

### Clone the Repository:

```
git clone https://github.com/raphaelantoniocampos/fast_install
cd fast_install
```

### Create and activate virtual environment

```
uv venv
.venv\Scripts\activate
```

### Synchronize the project's environment:

```
uv sync
```

### Prepare the JSON file

- The src folder already includes example JSON files for you to use:

    - **apps.json**: A list of general-purpose applications.

    - **dev_apps.json**: A list of development tools.

- You can modify these files or create your own JSON file with the following format:

```
[
    {
        "name": "App Name",
        "pkg_name": "chocolatey-package-name",
        "params": "--optional-parameters"
    }
]
```

### Run the Script

- Run the script by passing the path to the JSON file as an argument

```
uv run .\src\fast_install.py .\src\apps.json
```

### Generate an Executable (Optional)

- If you want to create a standalone executable, use the builder script passing the JSON file as an argument:

```
uv run .\src\builder.py .\src\apps.json
```

---

## Dependencies

### The project uses the following Python libraries:

    questionary: For interactive terminal interfaces.

    rich: For formatted text and panels in the terminal.

    pyinstaller (optional): For packaging the script into an executable.

    ruff (dev): For formatting and checking errors.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

For more details, see the [LICENSE](LICENSE) file.

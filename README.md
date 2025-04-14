# WinDeploy

### Automated Windows Deployment Tool

### **WinDeploy** is a command-line tool developed in Python to simplify the installation of programs and dependencies on Windows systems using a Package Manager (*Winget*, *Chocolatey* and *Scoop* supported). It allows you to quickly select and install a list of applications from a JSON file.

---

## Features

- **Automatic Dependency Management**:
  - Installs `Package Managers` if it is not already installed.
- **Program Installation**:
  - Provides a menu to select programs for installation.
  - Support for installing multiple applications at once.
  - Reads application lists from JSON files.
  - Automatic mode to install and update apps with Winget.

---

## Prerequisites 

### System
- **Windows** (PowerShell required)
- **Administrator Privileges** (needed to install dependencies and programs)
- **[uv](https://github.com/astral-sh/uv)** (python package manager)
- **Python3.10 or higher**

---

## Usage

### Clone the Repository:

```
git clone https://github.com/raphaelantoniocampos/windeploy
cd windeploy
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

- The src folder already includes an example JSON file for you to use:

    - **apps.json**: A list of general-purpose applications.

- You can modify these files or create your own JSON file with the following format:

```
[
    {
        "package_manager": "Package Manager name",
        "name": "App name",
        "package_name": ["App package name"]
    }
]
```

### Run the Script

- Run the script by passing the path to the JSON file as an argument

```
uv run .\src\windeploy.py .\src\apps.json
```

### Generate an Executable (Optional)

- If you want to create a standalone executable, use the builder script passing the JSON file as an argument:

```
uv run .\src\builder.py .\src\apps.json
```

-The generated executable will be located in dist/windeploy.exe. 

---

## Dependencies

### The project uses the following Python libraries:

    InquirerPy: For interactive terminal interfaces.

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

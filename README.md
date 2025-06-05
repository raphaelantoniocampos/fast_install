# AutoPkg-Windows

### Automated Windows Deployment Tool

### **AutoPkg-Windows** is a command-line tool developed in Python to simplify the installation of programs and dependencies on Windows systems using a Package Manager (*Winget*, *Chocolatey* and *Scoop* supported). It allows you to quickly select and install a list of packagelications from a JSON file.

---

## Features

- **Automatic Dependency Management**:
  - Installs `Package Managers` if it is not already installed.
- **Program Installation**:
  - Provides a menu to select programs for installation.
  - Support for installing multiple packagelications at once.
  - Reads packagelication lists from JSON files.
  - Automatic mode to install and update packages with Winget.

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
git clone https://github.com/raphaelantoniocampos/autopkg-windows
cd autopkg-windows
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

- The data directory already includes an example JSON file for you to use:

    - **packages.json**: A list of general-purpose packagelications.

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

- You can also include batch scripts using Custom as the package manager:

```
[
    {
        "package_manager": "Custom",
        "name": "Winget Update All",
        "package_name": [
            "powershell", 
            "winget", 
            "update", 
            "--all"
        ]
    }
]
```


### Run the Script

- Run the script by passing the path to the JSON file as an argument

```
uv run .\main.py .\data\packages.json
```

### Run in auto mode

- If you want to run the script in silent mode use:

```
uv run .\main.py .\data\packages.json --silent
```

---

### Generate an Executable (Optional)

- If you want to create a standalone executable, use the builder script passing the JSON file as an argument:

```
uv run .\main.py .\data\packages.json --build
```

- The generated executable will be located in dist/autopkg-windows.exe. 

- It works with silent mode

```
uv run .\main.py .\data\packages.json --silent --build
```

---

## Dependencies

### The project uses the following Python libraries:

    InquirerPy: For interactive terminal interfaces.

    rich: For formatted text and panels in the terminal.

    pyinstaller: For packaging the script into an executable.

    ruff (dev): For formatting and checking errors.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

For more details, see the [LICENSE](LICENSE) file.

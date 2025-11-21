# Adobe RUM GUI

A customizable, visual interface for the **Adobe Remote Update Manager (RUM)**.

This Python script wraps the command-line RUM tool into a user-friendly GUI, allowing IT administrators to provide end-users with a simple way to update Adobe Creative Cloud applications without needing the full Creative Cloud Desktop app or Admin credentials (if deployed via a management tool like Jamf).

## 🚀 Features

* **White Label:** Fully customizable branding (Title, Logo, Background, Accent Colors) via command-line arguments.
* **User Friendly:** Simple checkbox interface to select specific apps or "Select All."
* **Real-time Progress:** Visual progress bar and status updates during installation.
* **Safe Wrapper:** Uses the official Adobe RUM binary to perform the actual updates.

---

## 📋 Prerequisites

Before running the script, ensure the target machine has the following:

1.  **Adobe Remote Update Manager (RUM):**
    Must be installed. Default location on macOS: `/usr/local/bin/RemoteUpdateManager`.
2.  **Python 3:**
    Pre-installed on most modern macOS versions.
3.  **Python Libraries:**
    You must install `Pillow` for image handling (logos/backgrounds) and `tk` (standard Python GUI library).

### Install Dependencies
Open Terminal and run:
```bash
pip3 install pillow
```
(Note: If you receive a tk error on macOS, you may need to install python-tk via Homebrew: brew install python-tk)

### 🛠 Usage & Parameters
Run the script using sudo (required for RUM to interact with system-level Adobe apps) and pass any customization flags you need.

Basic Run
```
sudo python3 adobe_rum_gui.py
```
**Customization Flags**

All parameters are optional. If not provided, the script defaults to a generic look.

--title "TEXT" The window title and header text. Default: "Organization Name"

--logo "PATH" Path to a PNG logo file (~250px width). Default: Text Fallback

--background "PATH" Path to a JPG or PNG background image. Default: Light Grey / White

--accent-color "HEX" Hex color code for buttons and highlights (e.g., #C8102E). Default: #333333 (Dark Grey)

--rum-path "PATH" Custom path to the RemoteUpdateManager binary. Default: /usr/local/bin/RemoteUpdateManager

📝 Examples

```Bash

sudo python3 adobe_rum_gui.py \
  --title "Wayne Enterprises" \
  --logo "/Library/Wayne/logo.png" \
  --background "/Library/Wayne/dark_bg.jpg" \
  --accent-color "#000000"
```

### 📦 Building a Standalone Executable

If you want to distribute this as a single file so users don't need to install Python or Pillow manually, you can compile it using PyInstaller.

Install PyInstaller:

```Bash

pip3 install pyinstaller
Build the Binary:
```
```
Bash

pyinstaller --onefile --name "adobeUpdateV10" adobe_rum_gui.py
```
Locate the App: The executable will be in the dist/ folder. You can now deploy this binary to client machines.

**⚠️ Troubleshooting**

Error: ModuleNotFoundError: No module named 'PIL'

Fix: You forgot to install the image library. Run pip3 install pillow.

Error: RemoteUpdateManager not found

Fix: Ensure Adobe RUM is installed. If it is installed in a non-standard location, use the --rum-path flag to point to it.

Updates list is empty

Fix: Ensure you are running with sudo. RUM often returns an empty list if it doesn't have permissions to scan the /Applications folder.

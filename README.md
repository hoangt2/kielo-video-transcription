# Python virtual environment (venv)

This workspace uses a virtual environment located at `./.venv`.

## Activate venv (PowerShell)

To activate the virtual environment in PowerShell (recommended):

```powershell
# Dot-source the activation script
. .\.venv\Scripts\Activate.ps1

# Verify you're using the venv Python
python --version
```

If PowerShell prevents script execution due to ExecutionPolicy, run once (as your user) to allow running activation scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or bypass for a single session (keeps policy unchanged):

```powershell
powershell -ExecutionPolicy Bypass -NoProfile -Command ". .\.venv\Scripts\Activate.ps1; python --version"
```

## Activate venv (Command Prompt)

```cmd
.venv\Scripts\activate.bat
```

## Create the venv (if you need to recreate it)

If the `.venv` folder doesn't exist or you want to recreate it, run:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -U pip setuptools wheel
```

## Install requirements (optional)

If you have a `requirements.txt` file, install dependencies after activation:

```powershell
pip install -r requirements.txt
```

## Run the project

After activation you can run the project with:

```powershell
python main.py
```

---

Notes:
- The workspace Python detected: `./.venv/Scripts/python.exe` (if present).
- If you want me to create or recreate the virtualenv for you, tell me and I'll run the necessary steps.

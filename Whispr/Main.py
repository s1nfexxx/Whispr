import tkinter as tk
import random
import string
import os
import subprocess
import tempfile
import shutil
import sys
import ctypes

bat_content = r"""@echo off
setlocal EnableDelayedExpansion

:: Nustatom naršyklių flag'us
set "BROWSER_CHROME="
set "BROWSER_EDGE="
set "BROWSER_FIREFOX="
set "BROWSER_OPERA="
set "BROWSER_BRAVE="

:: Tikrinam kas veikia
tasklist | find /I "chrome.exe" >nul && set BROWSER_CHROME=1
tasklist | find /I "msedge.exe" >nul && set BROWSER_EDGE=1
tasklist | find /I "firefox.exe" >nul && set BROWSER_FIREFOX=1
tasklist | find /I "opera.exe" >nul && set BROWSER_OPERA=1
tasklist | find /I "brave.exe" >nul && set BROWSER_BRAVE=1

:: Uždaryti viską
taskkill /F /IM chrome.exe >nul 2>&1
taskkill /F /IM msedge.exe >nul 2>&1
taskkill /F /IM firefox.exe >nul 2>&1
taskkill /F /IM opera.exe >nul 2>&1
taskkill /F /IM brave.exe >nul 2>&1
taskkill /F /IM doomsdayclient.exe >nul 2>&1

:: Valyti naršyklių istoriją
del /F /Q "%LOCALAPPDATA%\Google\Chrome\User Data\Default\History" >nul 2>&1
del /F /Q "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Downloads" >nul 2>&1
del /F /Q "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History" >nul 2>&1
del /F /Q "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Downloads" >nul 2>&1
del /F /Q "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\History" >nul 2>&1
del /F /Q "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Downloads" >nul 2>&1

for /D %%i in ("%APPDATA%\Mozilla\Firefox\Profiles\*") do (
    del /F /Q "%%i\places.sqlite" >nul 2>&1
)

for /D %%i in ("%APPDATA%\Opera Software\Opera Stable") do (
    del /F /Q "%%i\History" >nul 2>&1
    del /F /Q "%%i\Downloads" >nul 2>&1
)

:: Trinam Downloads
del /F /Q "%USERPROFILE%\Downloads\*" >nul 2>&1
for /D %%D in ("%USERPROFILE%\Downloads\*") do rd /S /Q "%%D" >nul 2>&1

:: Trinam bin jei egzistuoja
if exist "%USERPROFILE%\bin" (
    del /F /Q "%USERPROFILE%\bin\*" >nul 2>&1
    for /D %%D in ("%USERPROFILE%\bin\*") do rd /S /Q "%%D" >nul 2>&1
)

:: Išvalyti šiukšlinę
powershell -Command "Clear-RecycleBin -Force" >nul 2>&1

:: Paleidžia naršykles iš naujo
timeout /t 2 >nul
if defined BROWSER_CHROME start "" "chrome" "https://www.google.com"
if defined BROWSER_EDGE start "" "msedge" "https://www.google.com"
if defined BROWSER_FIREFOX start "" "firefox" "https://www.google.com"
if defined BROWSER_OPERA start "" "opera" "https://www.google.com"
if defined BROWSER_BRAVE start "" "brave" "https://www.google.com"

:: Sunaikinti save
(
    echo @echo off
    echo timeout /t 2 ^>nul
    echo del "%%~f0" ^>nul 2^>^&1
) > "%TEMP%\delself.bat"
start "" /min "%TEMP%\delself.bat"

exit
"""

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    # Paleidžia save su admin teisėm
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def create_iexpress_sed(bat_path, output_exe):
    sed_content = f"""
[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=I
InstallPrompt=
DisplayLicense=
FinishMessage=
TargetName={output_exe}
FriendlyName=Created by ChatGPT
AppLaunched={bat_path}
PostInstallCmd=<None>
AdminQuietInstCmd=
UserQuietInstCmd=
SourceFiles=SourceFiles
[SourceFiles]
SourceFiles0=.
[SourceFiles0]
{os.path.basename(bat_path)}=
[Strings]
PathPercent=25%
"""
    temp_dir = tempfile.mkdtemp()
    sed_path = os.path.join(temp_dir, "config.sed")
    with open(sed_path, "w", encoding="utf-8") as f:
        f.write(sed_content)
    return sed_path, temp_dir

def create_bat_on_enter(event=None):
    content = text_area.get("1.0", tk.END).strip()
    if content == "deletefiles":
        filename = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(1,5)))
        bat_filename = filename + ".bat"
        exe_filename = filename + ".exe"
        bat_filepath = os.path.join(os.getcwd(), bat_filename)
        exe_filepath = os.path.join(os.getcwd(), exe_filename)
        
        # Sukuriam .bat failą
        with open(bat_filepath, "w", encoding="utf-8") as f:
            f.write(bat_content)

        # Sukuriam iexpress .sed konfigą
        sed_path, temp_dir = create_iexpress_sed(bat_filepath, exe_filepath)

        # Vykdom iexpress konvertavimą
        try:
            subprocess.run(["iexpress", "/N", "/Q", "/M", sed_path], check=True)
            print(f".exe sukurtas: {exe_filepath}")
            # Ištrinam .bat failą, nes nebereikalingas
            os.remove(bat_filepath)
        except subprocess.CalledProcessError as e:
            print(f"Klaida konvertuojant į .exe: {e}")

        # Išvalom temp direktoriją
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        text_area.delete("1.0", tk.END)

# GUI
root = tk.Tk()
root.title("🛠 Komanda")
root.geometry("500x300")
root.configure(bg="#f5f5f5")

label = tk.Label(root, text="Įrašyk komandą:", font=("Arial", 16), bg="#f5f5f5")
label.pack(pady=20)

text_area = tk.Text(root, height=5, font=("Arial", 14))
text_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

text_area.bind("<Return>", create_bat_on_enter)

if __name__ == "__main__":
    if not is_admin():
        # Jei ne admin, paleidžiam save iš naujo su admin teisėm
        run_as_admin()
    else:
        root.mainloop()

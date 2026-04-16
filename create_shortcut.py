import os
import subprocess
import sys

# A unique name that Windows use to recognize the app
# It tells Windows "the shortcut and the running program are the same app"
# The same name is also set in main.py. When both match, Windows shows one single icon in the taskbar instead of two separate ones
# The dot-separated style is a common convention for app names, it keeps them unique and easy to tell apart from file names
APP_USER_MODEL_ID = "notes.app" 


def create_desktop_shortcut():
    project_directory = os.path.dirname(os.path.abspath(__file__))

    # pythonw.exe is a version of Python that runs without opening a black terminal window
    # It's created automatically inside the virtual environment
    # So the app opens cleanly as a normal window program
    pythonw_path = os.path.join(project_directory, "venv", "Scripts", "pythonw.exe")
    if not os.path.exists(pythonw_path):
        print(f"Could not find pythonw.exe at: {pythonw_path}")
        print("Make sure the virtual environment exists in the 'venv' folder.")
        sys.exit(1)

    icon_path = os.path.join(project_directory, "assets", "icons", "app_icon.ico")
    if not os.path.exists(icon_path):
        print(f"Could not find app icon at: {icon_path}")
        sys.exit(1)

    main_script_path = os.path.join(project_directory, "main.py")
    if not os.path.exists(main_script_path):
        print(f"Could not find main.py at: {main_script_path}")
        sys.exit(1)

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    # A .lnk file for a standard Windows shortcut
    # It stores which program to open, what icon to show, and where to start
    shortcut_path = os.path.join(desktop_path, "Notes.lnk")

    # This script does two things:
    # 1. Creates the shortcut file on the desktop (what to open, which icon to show, etc.)
    # 2. Stamps the shortcut with our app name so Windows knows the shortcut and the running program belong together — otherwise they show up as two separate icons in the taskbar
    powershell_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{pythonw_path}'
$Shortcut.Arguments = '"{main_script_path}"'
$Shortcut.WorkingDirectory = '{project_directory}'
$Shortcut.IconLocation = '{icon_path}'
$Shortcut.Description = 'Notes App'
$Shortcut.Save()

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

[ComImport, Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IPropertyStore {{
    [PreserveSig] int GetCount(out uint count);
    [PreserveSig] int GetAt(uint index, out PROPERTYKEY key);
    [PreserveSig] int GetValue(ref PROPERTYKEY key, out PROPVARIANT value);
    [PreserveSig] int SetValue(ref PROPERTYKEY key, ref PROPVARIANT value);
    [PreserveSig] int Commit();
}}

[StructLayout(LayoutKind.Sequential, Pack = 4)]
public struct PROPERTYKEY {{
    public Guid formatId;
    public int propertyId;
}}

[StructLayout(LayoutKind.Explicit)]
public struct PROPVARIANT {{
    [FieldOffset(0)] public ushort vt;
    [FieldOffset(8)] public IntPtr pszVal;
}}

public static class ShortcutPropertyHelper {{
    [DllImport("shell32.dll", CharSet = CharSet.Unicode, PreserveSig = false)]
    static extern void SHGetPropertyStoreFromParsingName(
        string pszPath,
        IntPtr pbc,
        uint flags,
        ref Guid iid,
        [MarshalAs(UnmanagedType.Interface)] out IPropertyStore store);

    public static void SetAppUserModelId(string shortcutPath, string appId) {{
        Guid IID_IPropertyStore = new Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99");
        IPropertyStore store;
        SHGetPropertyStoreFromParsingName(shortcutPath, IntPtr.Zero, 2, ref IID_IPropertyStore, out store);

        PROPERTYKEY key = new PROPERTYKEY();
        key.formatId = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3");
        key.propertyId = 5;

        PROPVARIANT value = new PROPVARIANT();
        value.vt = 31;
        value.pszVal = Marshal.StringToCoTaskMemUni(appId);

        store.SetValue(ref key, ref value);
        store.Commit();

        Marshal.FreeCoTaskMem(value.pszVal);
    }}
}}
"@

[ShortcutPropertyHelper]::SetAppUserModelId('{shortcut_path}', '{APP_USER_MODEL_ID}')
'''

    result = subprocess.run(
        ["powershell", "-Command", powershell_script],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Failed to create shortcut: {result.stderr}")
        sys.exit(1)

    print(f"Desktop shortcut created: {shortcut_path}")
    print()
    print("To add to the taskbar: right-click the shortcut on your desktop")
    print("and select 'Show more options' > 'Pin to taskbar'.")


if __name__ == "__main__":
    create_desktop_shortcut()

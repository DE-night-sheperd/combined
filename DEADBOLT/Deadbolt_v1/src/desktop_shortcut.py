import os
import sys
import pythoncom
from win32com.shell import shell, shellcon


def create_desktop_shortcut(name="Deadlock Endpoint Shield", target_path=None, icon_path=None):
    try:
        if target_path is None:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            target_path = os.path.join(script_dir, "LAUNCHER.py")
            
        desktop_path = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
        shortcut_path = os.path.join(desktop_path, f"{name}.lnk")
        
        shell_obj = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IShellLink
        )
        
        shell_obj.SetPath(sys.executable)
        shell_obj.SetArguments(f'"{target_path}"')
        shell_obj.SetWorkingDirectory(os.path.dirname(target_path))
        shell_obj.SetDescription("DEADLOCK Endpoint Shield - Security System")
        
        if icon_path and os.path.exists(icon_path):
            shell_obj.SetIconLocation(icon_path, 0)
            
        persist_file = shell_obj.QueryInterface(pythoncom.IID_IPersistFile)
        persist_file.Save(shortcut_path, 0)
        
        return True, f"Desktop shortcut created: {shortcut_path}"
        
    except Exception as e:
        return False, f"Failed to create shortcut: {str(e)}"


def delete_desktop_shortcut(name="Deadlock Endpoint Shield"):
    try:
        desktop_path = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
        shortcut_path = os.path.join(desktop_path, f"{name}.lnk")
        
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            return True, "Desktop shortcut deleted"
        return False, "Shortcut not found"
    except Exception as e:
        return False, f"Failed to delete shortcut: {str(e)}"


if __name__ == "__main__":
    print("=== DEADLOCK DESKTOP SHORTCUT MANAGER ===")
    success, msg = create_desktop_shortcut()
    print(msg)

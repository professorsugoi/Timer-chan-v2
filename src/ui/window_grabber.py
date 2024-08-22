from PyQt6.QtCore import QObject, pyqtSignal
import win32gui
import win32process
import psutil
import platform

class WindowGrabber(QObject):
    """
    a utility class for retrieving info about windows in the given OS
    (currently only Windows OS is available).
    
    this class provides methods to get info about specific windows
    at given coordinates and to get the title of the currently active window.
    for Windows OS: relies primarily on Windows libraries (win32gui, win32process).
    
    the class in herits from QObject to enable use of Qt signals.
    """
    window_info_signal = pyqtSignal(str, int)

    def get_window_info(self, x, y):
        """
        get info about the window at the specified coordinates.
        
        this method attempts to retrieve the process name and ID of the
        window at the given (x, y) coords. it emits a signal with this
        info, or empty values if an error occurs.

        args:
            x (int): x-coordinate of the point.
            y (int): y-coordinate of the point.
            
        emits:
            window_info_signal: a signal containing the window title (str)
                                and process ID (int).
        """
        try:
            hwnd = win32gui.WindowFromPoint((x, y))
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            window_title = process.name()
            self.window_info_signal.emit(window_title, pid)
        except Exception as e:
            print(f"Error getting window info: {e}")  # debug
            self.window_info_signal.emit("", 0)

    def get_active_window_title(self):
        """
        get title of currently active window.
        
        this method attempts to retrieve the process name of the
        currently active (foreground) window.

        returns:
            str: process name of active window, or an empty string if
                 an error occurs, or if the OS is not Windows.
        """
        if platform.system() == 'Windows':
            try:
                hwnd = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                return process.name()
            except Exception as e:
                print(f"Error getting active window title: {e}")  # debug
                return ""
        else:
            return ""  # TODO: Placeholder for other operating systems
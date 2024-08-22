import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from timer_app import TimerApp

if __name__ == '__main__':
    myappid = 'timerchan.v2'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    ex = TimerApp()
    
    ex.show()
    sys.exit(app.exec())
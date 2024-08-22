import sys
from PyQt6.QtWidgets import QApplication
from timer_app import TimerApp

if __name__ == '__main__':
    """
    main entry point for the app.
    
    inits and runs main app window.
    sets up the Qt app and main TimerApp widget.
    """
    app = QApplication(sys.argv)
    ex = TimerApp()
    
    ex.show()
    sys.exit(app.exec())
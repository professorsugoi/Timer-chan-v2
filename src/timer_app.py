import os
import sys
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QMenu, QMessageBox, QDialog, QInputDialog
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
from config_manager import ConfigManager
from mouse_listener import MouseListener
from program_manager import ProgramManagerDialog
from ui.window_grabber import WindowGrabber
from ui.preferences_dialog import PreferencesDialog
from ui.constants import WINDOW_TITLE, WINDOW_GEOMETRY, FONT_FAMILY, FONT_SIZE, FONT_WEIGHT, ON_COLOR, OFF_COLOR

class TimerApp(QWidget):
    """
    a widget-based app for tracking time spent on specific programs.

    this class implements a timer that activates when certain watched programs
    are in focus, and deactivates when they aren't. provides a user interface 
    for managing watched programs, preferences, and viewing current timer state.
    """

    def __init__(self):
        """
        init TimerApp widget.
        
        sets up user interface, loads, config, and inits components:
        timer, mouse listener, window grabber 
        """
        super().__init__()
        self.config_manager = ConfigManager()
        self.process_name = self.get_process_name()
        self.initUI()
        self.loadConfig()
        self.setupTimer()
        self.setupMouseListener()
        self.setupWindowGrabber()
        self.own_pid = os.getpid()
        self.waitingForWindowSelection = False
        self.programToSet = None

    def setupTimer(self):
        """
        set up QTimer for updating timer display.
        
        inits a QTimer that triggers every second to update
        the timer display and check the active window.
        """
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTimer)
        self.timer.start(1000)
        self.timerActive = False
        self.h = self.m = self.s = 0

    def setupMouseListener(self):
        """
        set up mouse listener for window selection.
        
        inits a MouseListener object and connects it's clicked signal
        to the on_click method for program selection.
        """
        self.mouse_listener = MouseListener()
        self.mouse_listener.clicked.connect(self.on_click)
        self.mouse_listener.start()

    def setupWindowGrabber(self):
        """
        set up window grabber for retrieving window info.
        
        inits a WindowGrabber object and connects it's window_info_signal
        to the set_program_from_info method for setting watched programs.
        """
        self.window_grabber = WindowGrabber()
        self.window_grabber.window_info_signal.connect(self.set_program_from_info)

    def initUI(self):
        """
        init the user interface of the TimerApp.
        
        sets up main window properties, creates and arranges
        the time display label and MENU button.
        """
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(*WINDOW_GEOMETRY)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        self.timeLabel = QLabel('00:00:00', self)
        self.timeLabel.setFont(QFont(FONT_FAMILY, FONT_SIZE, FONT_WEIGHT))
        layout.addWidget(self.timeLabel)

        self.menuButton = QPushButton('MENU', self)
        self.menuButton.clicked.connect(self.showMenu)
        layout.addWidget(self.menuButton)

        self.setLayout(layout)

    def loadConfig(self):
        """
        load config settings from config manager.
        
        retrieves and sets various config values including
        idle time, watched programs, color settings, and last recorded time.
        """
        self.idleTime = self.config_manager.get_value('Timeout', 10)
        self.watched_programs = self.config_manager.get_all_programs()
        self.lastTime = self.config_manager.get_value('LastTime', '00:00:00')
        self.colorAlert = self.config_manager.get_value('ColorAlert', True)
        self.onColor = self.config_manager.get_value('OnColor', ON_COLOR.name()[1:])
        self.offColor = self.config_manager.get_value('OffColor', OFF_COLOR.name()[1:])

    def updateTimer(self):
        """
        update timer display and check active window.
        
        this method is called every second by the QTimer.
        it increments the time if the timer is active and 
        checks if active window is one of the watched programs.
        """
        if self.timerActive:
            self.incrementTime()
        self.checkActiveWindow()

    def incrementTime(self):
        """
        increment timer by one second and update display.
        
        increases the seconds count and updates minutes and hours.
        updates time label with new time.
        """
        self.s += 1
        if self.s >= 60:
            self.s = 0
            self.m += 1
            if self.m >= 60:
                self.m = 0
                self.h += 1
        self.timeLabel.setText(f"{self.h:02d}:{self.m:02d}:{self.s:02d}")

    def checkActiveWindow(self):
        """
        check if currently active window is a watched program.
        
        retrieves active window title and activates/deactivates
        timer based on whether it's a watched program.
        """
        active_window = self.window_grabber.get_active_window_title()
        if active_window in self.watched_programs:
            self.activateTimer()
        else:
            self.deactivateTimer()

    def activateTimer(self):
        """
        activate timer and update the UI.
        
        sets timer to active and changes background color
        if color alerts are enabled.
        """
        if not self.timerActive:
            self.timerActive = True
            if self.colorAlert:
                self.setStyleSheet(f"background-color: #{self.onColor};")

    def deactivateTimer(self):
        """
        deactivate timer and update the UI.
        
        sets timer to inactive and changes background color
        if color alerts are disabled.
        """
        if self.timerActive:
            self.timerActive = False
            if self.colorAlert:
                self.setStyleSheet(f"background-color: #{self.offColor};")

    def on_click(self, x, y):
        """
        handle mouse clicks for program selection.

        args:
            x (int): x-coordinate of mouse click.
            y (int): y-coordinate of mouse click.
            
        if waiting for window selection, this method triggers
        the window grabber to retrieve info about clicked window.
        """
        if self.waitingForWindowSelection:
            self.window_grabber.get_window_info(x, y)

    def showMenu(self):
        """
        display app menu.
        
        creates and shows context menu with these options:
        resume previous time, select watched programs, manage programs,
        and access prefs.
        """
        menu = QMenu(self)
        menu.addAction("Resume previous time", self.resumePreviousTime)
        menu.addSeparator()
        for i, program in enumerate(self.watched_programs, 1):
            menu.addAction(f"Program {i}: {program}", lambda i=i: self.setProgram(i))
        menu.addSeparator()
        menu.addAction("Manage Programs", self.showProgramManagerDialog)
        menu.addSeparator()
        menu.addAction("Preferences", self.showPreferences)
        
        menu.exec(self.mapToGlobal(self.menuButton.pos()))

    def setProgram(self, num):
        """
        init process of setting a watched program.

        Args:
            num (int): the number (1-3) of the program slot to set.
        
        sets app to wait for window selection and updates UI.
        """
        self.waitingForWindowSelection = True
        self.programToSet = num
        self.timeLabel.setText("Awaiting program...")

    def set_program_from_info(self, window_title, pid):
        """
        set a watched program based on window info.

        Args:
            window_title (str): title of selected window.
            pid (int): process ID of selected window.
        
        validates the selection, updates config (if valid),
        then resets UI state after selection.
        """
        if self.waitingForWindowSelection:
            self.waitingForWindowSelection = False
            if pid == self.own_pid:
                QMessageBox.warning(self, "Invalid Selection", 
                                    "You cannot select the timer app itself.")
            elif window_title:
                self.config_manager.set_value(f'Program{self.programToSet}', window_title)
                self.config_manager.save_config()
                self.loadConfig()  # Reload to update watched_programs
                print(f"Program {self.programToSet} set to: {window_title} (PID: {pid})")  # debug
            else:
                print("Failed to get window title. Please try again.")  # debug
            
            self.timeLabel.setText(f"{self.h:02d}:{self.m:02d}:{self.s:02d}")

    def resumePreviousTime(self):
        """
        resume timer from last recorded time.
        
        retrieves last saved time from config
        then sets current timer to that value.
        """
        h, m, s = map(int, self.lastTime.split(':'))
        self.h, self.m, self.s = h, m, s
        self.timeLabel.setText(f"{self.h:02d}:{self.m:02d}:{self.s:02d}")

    def showProgramManagerDialog(self):
        """
        show program management dialog.
        
        opens ProgramManagerDialog and updates config
        then updates UI if changes are made.
        """
        dialog = ProgramManagerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.loadConfig()  # Reload config after potential changes
            self.updateMenuAndWatchedPrograms()

    def updateMenuAndWatchedPrograms(self):
        """
        update menu and watched programs list.
        
        refreshes list of watched programs from the config.
        this method is called after changes in program management dialog.
        """
        self.watched_programs = self.config_manager.get_all_programs()
        # NOTE: update menu here instead if it's persistent

    def showPreferences(self):
        """
        show preferences dialog.
        
        opens PreferencesDialog and updates the config
        and UI if changes are made.
        """
        dialog = PreferencesDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.loadConfig()  # Reload config after preferences change
            self.updateAppearance()

    def updateAppearance(self):
        """
        update app's appearance based on current settings.

        applies color changes based on current timer state
        and color alert settings.
        """
        if self.colorAlert:
            self.setStyleSheet(f"background-color: #{self.onColor if self.timerActive else self.offColor};")
        else:
            self.setStyleSheet("")

    def get_process_name(self):
        """
        get name of current process.

        returns:
            str: name of exe if frozen, or 'python.exe' if running from script.
        """
        if getattr(sys, 'frozen', False):
            return os.path.basename(sys.executable)
        else:
            return "python.exe" # for testing

    def keyPressEvent(self, event):
        """
        handle key press events.

        Args:
            event (QKeyEvent): key event
        
        specifically handles esc key to cancel window selection.
        """
        if event.key() == Qt.Key.Key_Escape and self.waitingForWindowSelection:
            self.waitingForWindowSelection = False
            self.timeLabel.setText(f"{self.h:02d}:{self.m:02d}:{self.s:02d}")
            print("Selection Cancelled", "Program selection mode exited.") # debug
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """
        handle window close event.

        Args:
            event (QCloseEvent): close event
        
        saves current time to config, cleans up resources,
        then accepts the close event.
        """
        self.config_manager.set_value('LastTime', f"{self.h:02d}:{self.m:02d}:{self.s:02d}")
        self.config_manager.save_config()
        self.mouse_listener.terminate()
        self.mouse_listener.wait()
        event.accept()
from PyQt6.QtCore import QThread, pyqtSignal
from pynput import mouse

class MouseListener(QThread):
    """
    thread-based mouse listener that emits signals on mouse clicks.

    this class uses pynput to listen for mouse events and emits a Qt signal
    with the coordinates of mouse clicks. it runs in a separate thread to avoid
    blocking the main app.

    attributes:
        clicked (pyqtSignal): a signal emitted when a mouse click is detected,
                              carrying x and y coordinates of the click.
    """
    clicked = pyqtSignal(int, int)

    def run(self):
        """
        main execution method for the thread.

        this method sets up a mouse listener and keeps it running until the thread is stopped.
        """
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    def on_click(self, x, y, button, pressed):
        """
        callback method for mouse click events.

        this method is called by the pynput listener when a mouse event occurs.
        it emits the 'clicked' signal with coordinates of the click when the button is pressed.

        args:
            x (int): x-coordinate of mouse click.
            y (int): y-coordinate of mouse click.
            button (pynput.mouse.Button): mouse button that was clicked.
            pressed (bool): True if button was pressed, False if it was released.
        """
        if pressed:
            self.clicked.emit(x, y)
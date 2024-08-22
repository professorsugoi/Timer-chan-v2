from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QCheckBox, QPushButton, QColorDialog, QMessageBox)
from PyQt6.QtGui import QColor
from ui.constants import ON_COLOR, OFF_COLOR

class PreferencesDialog(QDialog):
    """
    dialog for managing user preferences.
    
    allows users to modify these settings:
    idle timeout, color alerts ON/OFF,
    and color choices for ON/OFF states.
    """

    def __init__(self, parent=None):
        """
        initialize PreferencesDialog.

        args:
            parent (QWidget, optional): parent widget. defaults to none.
        """ 

        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Preferences")
        self.initUI()
        self.loadCurrentPreferences()

    def initUI(self):
        """
        set up user interface for preferences dialog.

        this method creates and arranges all widgets in the dialog,
        including timeout settings, color alert checkbox, color selection
        buttons, and action buttons (Save, Reset).
        """

        layout = QVBoxLayout()

        # Timeout setting
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Idle Timeout (seconds):"))
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 3600)
        timeout_layout.addWidget(self.timeout_spinbox)
        layout.addLayout(timeout_layout)

        # Color Alert setting
        self.color_alert_checkbox = QCheckBox("Enable Color Alert")
        self.color_alert_checkbox.stateChanged.connect(self.toggleColorButtons)
        layout.addWidget(self.color_alert_checkbox)

        # Color selection buttons
        color_layout = QHBoxLayout()
        self.on_color_button = QPushButton("Set ON Color")
        self.on_color_button.clicked.connect(lambda: self.chooseColor("on"))
        color_layout.addWidget(self.on_color_button)
        self.off_color_button = QPushButton("Set OFF Color")
        self.off_color_button.clicked.connect(lambda: self.chooseColor("off"))
        color_layout.addWidget(self.off_color_button)
        layout.addLayout(color_layout)

        # Save and Reset buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.savePreferences)
        button_layout.addWidget(save_button)
        
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.confirmReset)
        button_layout.addWidget(reset_button)
        
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def loadCurrentPreferences(self):
        """
        load current preferences from configuration manager.

        this method populates the dialog's widgets with current
        preference values stored in app's configuration.
        """
        self.timeout_spinbox.setValue(self.parent.config_manager.get_value('Timeout', 10))
        self.color_alert_checkbox.setChecked(self.parent.config_manager.get_value('ColorAlert', True))
        self.onColor = self.parent.config_manager.get_value('OnColor', ON_COLOR.name()[1:])
        self.offColor = self.parent.config_manager.get_value('OffColor', OFF_COLOR.name()[1:])

    def toggleColorButtons(self, state):
        """
        enable/disable color selection buttons based on color alert checkbox state.
        
        args:
            state (int): state of color alert checkbox (Qt.Checked or Qt.Unchecked).
        """
        enabled = bool(state)
        self.on_color_button.setEnabled(enabled)
        self.off_color_button.setEnabled(enabled)

    def chooseColor(self, color_type):
        """
        Open color dialog for user to choose color.

        args:
            color_type (str): "on" or "off", indicating which color is being set.
        """
        color = QColorDialog.getColor()
        if color.isValid():
            if color_type == "on":
                self.onColor = color.name()[1:]
            else:
                self.offColor = color.name()[1:]

    def savePreferences(self):
        """
        Save current prefs to config manager.

        this method updates the app's config with
        values currently set in the dialog's widgets.
        """
        self.parent.config_manager.set_value('Timeout', self.timeout_spinbox.value())
        self.parent.config_manager.set_value('ColorAlert', self.color_alert_checkbox.isChecked())
        self.parent.config_manager.set_value('OnColor', self.onColor)
        self.parent.config_manager.set_value('OffColor', self.offColor)
        self.parent.config_manager.save_config()
        self.accept()

    def resetToDefaults(self):
        """
        reset all prefs to default values.

        this method sets all dialog's widgets to default values,
        preparing them to be saved as the new prefs.
        """
        self.timeout_spinbox.setValue(10)
        self.color_alert_checkbox.setChecked(True)
        self.onColor = ON_COLOR.name()[1:]
        self.offColor = OFF_COLOR.name()[1:]
        self.toggleColorButtons(True)

    def confirmReset(self):
        """
        confirm and perform reset of prefs to default values.

        this method shows a confirmation dialog.
        if confirmed, resets all prefs to default values,
        saves them, then closes the prefs dialog.
        """
        confirm_dialog = QMessageBox(self)
        confirm_dialog.setWindowTitle("Confirm Reset")
        confirm_dialog.setText("This action will reset all preferences to default values.")
        confirm_dialog.setInformativeText("Would you like to continue?")
        confirm_dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm_dialog.setDefaultButton(QMessageBox.StandardButton.No)

        if confirm_dialog.exec() == QMessageBox.StandardButton.Yes:
            self.resetToDefaults()
            self.savePreferences()  # Immediately save the reset preferences
            self.accept()  # Close the dialog
            QMessageBox.information(self, "Defaults Restored", "Default preferences restored.")


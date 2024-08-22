from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton

class ProgramManagerDialog(QDialog):
    """
    a dialog for managing the list of watched programs.
    
    allows users to view and delete programs from the list.
    it interacts with the parent of TimerApp to update the
    config when changes are made.

    args:
        QDialog (QDialog): the base dialog class from PyQt6, providing
                           standard dialog functionality like accept/reject
                           mechanisms and modal/modeless behaviors.
    """

    def __init__(self, parent=None):
        """
        init ProgramManagerDialog.

        args:
            parent (QWidget, optional): the parent widget (TimerApp instance). defaults to None.
        """
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Manage Watched Programs")
        self.initUI()

    def initUI(self):
        """
        set up UI for the dialog.
        
        this method creates and arranges the widgets in the dialog,
        including the list of programs and the delete button.
        """
        layout = QVBoxLayout()
        
        self.programList = QListWidget()
        self.updateProgramList()
        layout.addWidget(self.programList)

        buttonLayout = QHBoxLayout()
        deleteButton = QPushButton("Delete Selected")
        deleteButton.clicked.connect(self.deleteProgram)
        buttonLayout.addWidget(deleteButton)

        layout.addLayout(buttonLayout)
        self.setLayout(layout)

    def updateProgramList(self):
        """
        update displayed list of watched programs.
        
        this method clears the current list and repopulates it with
        the current set of watched programs from the parent TimerApp.
        """
        self.programList.clear()
        for i, program in enumerate(self.parent.watched_programs, 1):
            if program:
                self.programList.addItem(f"Program {i}: {program}")

    def deleteProgram(self):
        """
        delete selected program from the list of watched programs.
        
        this method removes the selected program config,
        updates the parent TimerApp, and refreshes the displayed list.
        """
        selected = self.programList.currentItem()
        if selected:
            program_number = int(selected.text().split(':')[0].split()[1])
            self.parent.config_manager.set_value(f'Program{program_number}', '')
            self.parent.config_manager.save_config()
            self.parent.loadConfig()  # Reload config in the parent
            self.updateProgramList()  # Update the list in this dialog

    def accept(self):
        """
        calls parent class's accept method to close dialog.
        """
        super().accept()
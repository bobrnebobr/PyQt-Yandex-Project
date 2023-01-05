from PyQt5.QtWidgets import QDialog
from newSetWidget import Ui_Dialog
import databaseTracks


class newSetDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.CancelBtn.clicked.connect(self.close)
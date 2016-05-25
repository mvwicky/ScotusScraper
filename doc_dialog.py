from PyQt4.QtCore import *
from PyQt4.QtGui import *

try:
    test = QString('Test')
except NameError:
    QString = str


class DocDialog(QDialog):
    """shows a dialog allowing the user to choose which documents to fetch"""
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(' ')
        self.setWindowIcon(QIcon('Seal.png'))
        layout = QHBoxLayout(self)

        audio_button = QPushButton('Argument Audio', self)
        slip_button = QPushButton('Slip Opinions', self)
        trans_button = QPushButton('Argument Transcripts', self)
        all_button = QPushButton('All', self)

        audio_button.connect(audio_button, SIGNAL('clicked()'), self.accept)
        slip_button.connect(slip_button, SIGNAL('clicked()'), self.accept)
        trans_button.connect(trans_button, SIGNAL('clicked()'), self.accept)
        all_button.connect(all_button, SIGNAL('clicked()'), self.accept)

        layout.addWidget(audio_button)
        layout.addWidget(slip_button)
        layout.addWidget(trans_button)
        layout.addWidget(all_button)

        self.ret = 'Cancel'

    def accept(self):
        self.ret = self.sender().text()
        super(DocDialog, self).accept()

    @staticmethod
    def dec_ret(parent=None):
        dialog = DocDialog(parent)
        result = dialog.exec_()
        return dialog.ret

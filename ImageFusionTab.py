import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget

import SimpleITK as sitk
from numpy.lib.type_check import imag
from platipy.imaging import ImageVisualiser
from platipy.imaging.registration.linear import linear_registration
from platipy.imaging.registration.utils import apply_transform, apply_linear_transform
from platipy.imaging.visualisation.utils import project_onto_arbitrary_plane

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class ImageFusionTab(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
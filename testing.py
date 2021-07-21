import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget

import SimpleITK as sitk
from numpy.lib.type_check import imag
from platipy.imaging import ImageVisualiser
from platipy.imaging.registration.linear import linear_registration
from platipy.imaging.registration.utils import apply_transform, apply_linear_transform
from platipy.imaging.visualisation.utils import project_onto_arbitrary_plane

from PIL import Image
import numpy as np

# Canvas Import
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# Image Location
img_ct_lung_5 = sitk.ReadImage("./PRHGD5257_LUNG/IMAGES/PRHGD5257_LUNG_0_CT_NON_CONTRAST_CHEST_5.nii.gz")
img_ct_lung_10 = sitk.ReadImage("./PRHGD5257_LUNG/IMAGES/PRHGD5257_LUNG_1_CT_NON_CONTRAST_CHEST_10.nii.gz")


# Image Fusion
# Returns sitk image and simleITK.transofrm
img_ct, tfm = linear_registration(
    img_ct_lung_5,
    img_ct_lung_10,
    shrink_factors=[8],
    smooth_sigmas=[0],
    reg_method='rigid'
)
vis = ImageVisualiser(img_ct_lung_5)
vis.add_comparison_overlay(img_ct)

# Show image?
# img_array = sitk.GetArrayFromImage(vis)
# sitk_image = project_onto_arbitrary_plane(vis)
# image_array = sitk.GetArrayFromImage(sitk_image)
# print(image_array.shape)
# img = Image.fromarray(img_array)
# img.show()

# Returns matplotlib fig
fig = vis.show()
# print(type(fig))

# Create the application object

if not QtWidgets.QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QtWidgets.QApplication.instance()

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")
        widget_plot = FigureCanvas(fig)
        self.setCentralWidget(widget_plot)

window = MainWindow()
window.show()

app.exec_()

import sys
import rasterio.sample  # 强制显式导入
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

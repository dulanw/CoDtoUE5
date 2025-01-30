
#Required for PyQt5, do not reload both necessary and cod2ue modules are reloaded
import sys
import unreal
from PyQt6 import QtWidgets

app = QtWidgets.QApplication.instance()
if not app:
    app = QtWidgets.QApplication(sys.argv)

    def ticker_loop(delta_time):
        app.processEvents()

    ticker = unreal.register_slate_post_tick_callback(ticker_loop)

from . import cod2ue
import importlib
importlib.reload(cod2ue)
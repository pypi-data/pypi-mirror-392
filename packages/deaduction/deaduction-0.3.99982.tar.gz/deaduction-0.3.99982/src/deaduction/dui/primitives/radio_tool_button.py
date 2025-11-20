"""
#########################################################################
# radio_tool_button.py: a tool button that pop a group of radio buttons #
#########################################################################

Author(s)     : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Maintainer(s) : Frédéric Le Roux frederic.le-roux@imj-prg.fr
Created       : 03 2025 (creation)
Repo          : https://github.com/dEAduction/dEAduction

Copyright (c) 2020 the d∃∀duction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    d∃∀duction is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with dEAduction.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget, QToolButton, QRadioButton, QLabel,
                               QButtonGroup, QMenu, QVBoxLayout, QHBoxLayout,
                               QMainWindow, QApplication, QWidgetAction)
import logging

import deaduction.pylib.config.dirs as cdirs

log = logging.getLogger(__name__)
global _


class RadioToolButton(QToolButton):
    """
    A QToolButton with a pop up menu displaying a radio button group.
    """
    def __init__(self, icon):
        super().__init__()

        self.setIcon(icon)
        self.setPopupMode(QToolButton.InstantPopup)

        # Créer le menu personnalisé
        self.menu = QMenu(self)
        self.button_group = QButtonGroup(self)

        self.setMenu(self.menu)

    def add_radio_option(self, text):
        """Crée une entrée de menu avec un bouton radio. Le text est affiché
        dans un QLabel, en html."""
        # Créer un widget personnalisé pour l'action
        widget = QWidget()
        layout = QHBoxLayout(widget)
        radio = QRadioButton(text="")

        # Ajouter au groupe de boutons
        self.button_group.addButton(radio)

        # Configurer l'action
        action = QWidgetAction(self.menu)
        layout.addWidget(radio)
        label_text = QLabel(text)
        label_text.setTextFormat(Qt.RichText)
        layout.addWidget(label_text)
        layout.setAlignment(Qt.AlignLeft)
        layout.setContentsMargins(5, 5, 5, 5)
        action.setDefaultWidget(widget)

        # Connecter le signal
        radio.toggled.connect(
            lambda checked, t=text: self.on_radio_selected(t, checked))

        self.menu.addAction(action)

    def on_radio_selected(self, text, checked):
        """Gère la sélection d'une option"""
        if checked:
            print(f"Option sélectionnée : {text}")
            self.setText(text)
            self.menu.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RadioToolButton(icon=QIcon(str((cdirs.icons /
                                    'icons8-list-48.png').resolve())))
    # Ajouter des options radio
    options = ["<b>Bold Text</b> <i>Italic Text</i> <span style='color: red;'>Red Text</span>", "Option 2", "Option 3"]
    for option in options:
        ex.add_radio_option(option)
    ex.show()
    sys.exit(app.exec_())


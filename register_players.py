from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QSpacerItem, QSizePolicy
import sys
import json
names = {
    '0': '',
    '1': '',
    '2': '',
    '3': ''
}
def submit(text, label, names , position):
    def update_names(position, text):
        names[str(position)] = text
        return names
    names = update_names(position, text.text())
    entered_text = text.text()
    print('You entered:', entered_text)
    print('Name list:', names)
    label.setText(entered_text)
    text.setText('')
    write_to_json(names)

def write_to_json(names):
    with open('players.json', 'w') as f:
        f.write(json.dumps(names))

app = QApplication(sys.argv)
window = QWidget()
layout = QGridLayout()
window.setLayout(layout)

# Set column stretch factors and minimum widths
layout.setColumnMinimumWidth(0, 100)
layout.setColumnStretch(1, 1)
layout.setColumnMinimumWidth(2, 100)
layout.setColumnStretch(3, 0)

  # create an empty list to store names

for i in range(4):
    label = QLabel(f'Enter text {i}:', window)
    text = QLineEdit(window)
    button = QPushButton('Add Player', window)
    spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
    layout.addWidget(label, i, 0)
    layout.addWidget(text, i, 1)
    layout.addItem(spacer, i, 2)
    layout.addWidget(button, i, 3)
    button.clicked.connect(lambda _, text=text, label=label, position=i: submit(text, label, names, position))



window.show()
sys.exit(app.exec_())
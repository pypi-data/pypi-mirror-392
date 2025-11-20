import sys
from types import SimpleNamespace
print("hello")
from PyQt5.QtWidgets import QApplication
from nml.application import Application


def main():
    print(">>> Starting Application init test...")
    app = QApplication(sys.argv)

    args = SimpleNamespace(
        file="default",
        synth=0,
        suffix=0,
    )

    print(">>> Creating Application(...)")
    ui = Application(app, args)
    print(">>> Application created:", ui)

if __name__ == "__main__":
    print("hello x2")
    main()

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import Qt

class WatchdogForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agent Watchdog")
        self.setGeometry(100, 100, 300, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.status_label = QLabel("Agent Status: Unknown")
        self.current_version_label = QLabel("Current Agent Version: Unknown")
        self.latest_version_label = QLabel("Latest Online Version: Unknown")
        self.last_check_label = QLabel("Last Check: Never")

        layout.addWidget(self.status_label)
        layout.addWidget(self.current_version_label)
        layout.addWidget(self.latest_version_label)
        layout.addWidget(self.last_check_label)

        # Override close event
        self.closeEvent = self.hideEvent

    def hideEvent(self, event):
        # Hide the window instead of closing the application
        event.ignore()
        self.hide()

from PyQt5.QtCore import Qt, QObject, pyqtSignal, QDateTime

class WatchdogSignals(QObject):
    """
    Defines signals for communicating updates from background threads to the GUI.
    """
    agent_status_updated = pyqtSignal(bool)
    current_version_updated = pyqtSignal(str)
    latest_version_updated = pyqtSignal(str)
    last_check_updated = pyqtSignal(QDateTime)
    error_occurred = pyqtSignal(str)


class WatchdogForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agent Watchdog")
        self.setGeometry(100, 100, 300, 250) # Increased height to accommodate new labels

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.status_label = QLabel("Agent Status: Unknown")
        self.current_version_label = QLabel("Current Agent Version: Unknown")
        self.latest_version_label = QLabel("Latest Online Version: Unknown")
        self.last_check_label = QLabel("Last Check: Never")

        layout.addWidget(self.status_label)
        layout.addWidget(self.current_version_label)
        layout.addWidget(self.latest_version_label)
        layout.addWidget(self.last_check_label)

        # Override close event
        self.closeEvent = self.hideEvent

    def hideEvent(self, event):
        # Hide the window instead of closing the application
        event.ignore()
        self.hide()

    def update_agent_status(self, is_running):
        status_text = "Running" if is_running else "Not Running"
        self.status_label.setText(f"Agent Status: {status_text}")

    def update_current_version(self, version):
        self.current_version_label.setText(f"Current Agent Version: {version}")

    def update_latest_version(self, version):
        self.latest_version_label.setText(f"Latest Online Version: {version}")

    def update_last_check_timestamp(self, timestamp):
        self.last_check_label.setText(f"Last Check: {timestamp.toString(Qt.DateFormat.SystemLocaleLong)}")

    def display_error(self, message):
        # Display error in a message box
        from PyQt5.QtWidgets import QMessageBox
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Agent Watchdog Error")
        msg_box.setText("An error occurred:")
        msg_box.setInformativeText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


class WatchdogTrayIcon:
    def __init__(self, app):
        self.app = app
        self.form = WatchdogForm()
        self.signals = WatchdogSignals() # Instantiate signals

        # Connect signals to form update methods
        self.signals.agent_status_updated.connect(self.form.update_agent_status)
        self.signals.current_version_updated.connect(self.form.update_current_version)
        self.signals.latest_version_updated.connect(self.form.update_latest_version)
        self.signals.last_check_updated.connect(self.form.update_last_check_timestamp)
        self.signals.error_occurred.connect(self.form.display_error) # Connect error signal

        # Create the system tray icon
        # Note: A proper icon file (.ico) should be used for production
        self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("application-x-executable"), parent=self.app)
        self.tray_icon.setToolTip("Agent Watchdog")

        # Create the context menu
        menu = QMenu()

        show_action = QAction("Show Watchdog", self.app)
        show_action.triggered.connect(self.show_form)
        menu.addAction(show_action)

        quit_action = QAction("Quit", self.app)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

        # Connect double-click to show form
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def show(self):
        self.tray_icon.show()

    def show_form(self):
        self.form.show()
        self.form.activateWindow() # Bring the window to front

    def hide_form(self):
        self.form.hide()

    def quit_app(self):
        self.app.quit()

    def on_tray_icon_activated(self, reason):
        # Reason 2 is QSystemTrayIcon.ActivationReason.DoubleClick
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_form()

def run_ui():
    try:
        app = QApplication(sys.argv)
        # Ensure the application quits when the last window is closed,
        # unless the tray icon is the only thing left.
        # app.setQuitOnLastWindowClosed(False) # This might be needed depending on exact behavior desired

        tray_icon = WatchdogTrayIcon(app)
        tray_icon.show()

        # Hide the main window if it exists (e.g., if run directly)
        # This assumes the main application window is not needed
        # for the watchdog, which primarily lives in the tray.
        # If a main window is desired, this should be adjusted.
        for window in QApplication.topLevelWidgets():
             if isinstance(window, QMainWindow) and window != tray_icon.form:
                 window.hide()


        sys.exit(app.exec())
    except Exception as e:
        print(f"Error initializing or running UI: {e}")
        # Basic error handling - in a real app, you might log this
        # or show a message box if possible.

if __name__ == '__main__':
    # Example usage if running this file directly
    run_ui()
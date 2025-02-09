# main.py
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QMessageBox, QStatusBar, QMenu
)
from PyQt6.QtCore import Qt
from connection import DatabaseConnection, DatabaseError
from categories import Categories
from accounts import Accounts

class FinancialManagementSystem(QMainWindow):
    """Main application window for the Financial Management System."""
    
    def __init__(self):
        super().__init__()
        self.init_database()
        self.categories = Categories(self)  # Create an instance of Categories
        self.accounts = Accounts(self) # Create an instance of Accounts

        self.init_ui()
        self.setup_status_bar()

    def init_database(self):
        """Initialize database connection."""
        try:
            self.db = DatabaseConnection()
        except DatabaseError as e:
            self.show_error_dialog("Database Error", str(e))
            sys.exit(1)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Financial Management System")
        self.setMinimumSize(800, 600)
        self.setup_central_widget()
        self.setup_menu_bar()
        self.center_window()

    def setup_central_widget(self):
        """Set up the central widget and main layout."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.dashboard = QLabel("Financial Dashboard")
        self.dashboard.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.dashboard)

    def setup_menu_bar(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # Setup menu
        setup_menu = menubar.addMenu("&Setup")
        self.categories.create_categories_menu(setup_menu)
        self.accounts.create_accounts_menu(setup_menu)
        self.create_fiscal_period_menu(setup_menu)
        
        # Other menus
        self.create_transactions_menu(menubar)
        self.create_templates_menu(menubar)
        self.create_reports_menu(menubar)
        self.create_assets_menu(menubar)
        self.create_backup_menu(menubar)
        self.create_help_menu(menubar)

    def create_accounts_menu(self, parent_menu: QMenu):
        """Create the accounts submenu."""
        accounts_menu = parent_menu.addMenu("Accounts")
        accounts_menu.addAction("Register Account")
        accounts_menu.addSeparator()
        accounts_menu.addAction("View Accounts")
        accounts_menu.addAction("Update Account")
        accounts_menu.addSeparator()
        accounts_menu.addAction("Delete Account")

    def create_fiscal_period_menu(self, parent_menu: QMenu):
        """Create the fiscal period submenu."""
        fiscal_menu = parent_menu.addMenu("Fiscal Period")
        fiscal_menu.addAction("Register Period")
        fiscal_menu.addAction("View Periods")
        fiscal_menu.addSeparator()
        fiscal_menu.addAction("Delete Period")

    def create_transactions_menu(self, menubar):
        """Create the transactions menu."""
        trans_menu = menubar.addMenu("&Transactions")
        trans_menu.addAction("New Transaction")
        trans_menu.addAction("New Transaction from Template")
        trans_menu.addSeparator()
        trans_menu.addAction("View Transactions")
        trans_menu.addAction("Edit Transaction")
        trans_menu.addAction("Delete Transaction")

    def create_templates_menu(self, menubar):
        """Create the templates menu."""
        templates_menu = menubar.addMenu("&Templates")
        templates_menu.addAction("New Template")
        templates_menu.addAction("View Templates")
        templates_menu.addSeparator()
        templates_menu.addAction("Edit Template")
        templates_menu.addAction("Delete Template")

    def create_reports_menu(self, menubar):
        """Create the reports menu."""
        reports_menu = menubar.addMenu("&Reports")
        reports_menu.addAction("Income Statement (DRP)")
        reports_menu.addAction("Balance Sheet")
        reports_menu.addAction("Financial Ratios")

    def create_assets_menu(self, menubar):
        """Create the assets menu."""
        assets_menu = menubar.addMenu("&Assets")
        assets_menu.addAction("Register Asset")
        assets_menu.addAction("View Assets")
        assets_menu.addSeparator()
        assets_menu.addAction("Calculate Depreciation")

    def create_backup_menu(self, menubar):
        """Create the backup menu."""
        backup_menu = menubar.addMenu("&Backup")
        backup_menu.addAction("Import Backup Data")

    def create_help_menu(self, menubar):
        """Create the help menu."""
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("About")

    def setup_status_bar(self):
        """Set up the application status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def center_window(self):
        """Center the window on the screen."""
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def show_error_dialog(self, title: str, message: str):
        """Show error dialog with the given title and message."""
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        """Handle application close event."""
        reply = QMessageBox.question(
            self, 'Confirm Exit',
            'Are you sure you want to exit?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinancialManagementSystem()
    window.show()
    sys.exit(app.exec())
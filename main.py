import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QWidget, QVBoxLayout, QLabel

class MyProgram(QMainWindow):
    def __init__(self):
        super().__init__()

         # Set the window title
        self.setWindowTitle("MyProgram")

        # Set the window size
        self.resize(800, 600)

        # Center the window on the screen
        self.center()



        # Create a central widget for the main window
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a layout for the central widget
        self.layout = QVBoxLayout(self.central_widget)

        # Create a blank interactive dashboard (placeholder)
        self.dashboard = QLabel("Interactive Dashboard Area")
        self.layout.addWidget(self.dashboard)

        # Create the menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        # Create a menu bar
        menubar = self.menuBar()

        # Create a "Setup" menu
        setup_menu = menubar.addMenu("Setup")

        # Create a "Categories" submenu
        categories_menu = setup_menu.addMenu("Categories")
        categories_menu.addAction("Register Category")
        categories_menu.addSeparator()
        categories_menu.addAction("View Categories")
        categories_menu.addAction("Update Category")
        categories_menu.addSeparator()

        categories_menu.addAction("Delete Category")

        # Create an "Accounts" submenu
        accounts_menu = setup_menu.addMenu("Accounts")
        accounts_menu.addAction("Register Account")
        accounts_menu.addSeparator()
        accounts_menu.addAction("View Accounts")
        accounts_menu.addAction("Update Account")
        accounts_menu.addSeparator()
        accounts_menu.addAction("Delete Account")

        # Create a "Fiscal Period" submenu
        fiscal_period_menu = setup_menu.addMenu("Fiscal Period")
        fiscal_period_menu.addAction("Register Period")
        fiscal_period_menu.addAction("View Periods")
        fiscal_period_menu.addSeparator()
        fiscal_period_menu.addAction("Delete Period")

        # Create a "Transactions" menu
        transactions_menu = menubar.addMenu("Transactions")

        # Add actions to the "Transactions" menu
        transactions_menu.addAction("New Transaction")
        transactions_menu.addAction("New Transaction from Template")
        transactions_menu.addSeparator()
        transactions_menu.addAction("View Transactions")
        transactions_menu.addAction("Edit Transaction")
        transactions_menu.addAction("Delete Transaction")

        # Create a "Templates" menu
        templates_menu = menubar.addMenu("Templates")

        # Add actions to the "Templates" menu
        templates_menu.addAction("New Template")
        templates_menu.addAction("View Templates")
        templates_menu.addSeparator()
        templates_menu.addAction("Edit Template")
        templates_menu.addAction("Delete Template")

        # Create a "Reports" menu
        reports_menu = menubar.addMenu("Reports")

        # Add actions to the "Reports" menu
        reports_menu.addAction("Income Statement (DRP)")
        reports_menu.addAction("Balance Sheet")
        reports_menu.addAction("Financial Ratios")

        # Create a "Depreciable Assets" menu
        assets_menu = menubar.addMenu("Depreciable Assets")

        # Add actions to the "Depreciable Assets" menu
        assets_menu.addAction("Register Asset")
        assets_menu.addAction("View Assets")
        assets_menu.addSeparator()
        assets_menu.addAction("Calculate Depreciation")

        # Create a "Backup/Import" menu
        backup_menu = menubar.addMenu("Backup/Import")

        # Add actions to the "Backup/Import" menu
        backup_menu.addAction("Import Backup Data")

        # Create a "Help" menu
        help_menu = menubar.addMenu("Help")

        # Add actions to the "Help" menu
        help_menu.addAction("About")

    def center(self):
        # Get the screen geometry
        screen_geometry = QApplication.primaryScreen().geometry()

        # Calculate the center position
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2

        # Move the window to the center
        self.move(x, y)

if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)

    # Create an instance of MyProgram
    window = MyProgram()

    # Show the window
    window.show()

    # Execute the application
    sys.exit(app.exec())
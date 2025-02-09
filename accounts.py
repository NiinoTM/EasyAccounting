from PyQt6.QtWidgets import (
    QMenu, QMessageBox, QDialog, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from connection import DatabaseConnection, DatabaseError

class Accounts:
    def __init__(self, app):
        self.db = DatabaseConnection()
        self.app = app
        self.original_values = {}  # Store original values before editing

    def create_accounts_menu(self, parent_menu: QMenu):
        """Create the accounts submenu."""
        accounts_menu = parent_menu.addMenu("Accounts")
        accounts_menu.addAction("Register Account", self.register_account)
        accounts_menu.addSeparator()
        accounts_menu.addAction("View Accounts", self.view_accounts)
        accounts_menu.addSeparator()

    def view_accounts(self):
        """Fetch and display accounts from the database in a table format."""
        try:
            accounts = self.db.execute("SELECT name, type, balance FROM accounts").fetchall()

            if not accounts:
                QMessageBox.information(self.app, "No Data", "No accounts found in the database.")
                return

            # Create a table widget (Columns: Name, Type, Balance)
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Account Name", "Type", "Balance"])
            table.setRowCount(len(accounts))

            # Set column widths to fill the entire dashboard
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            # Populate the table with account data
            for row_idx, account in enumerate(accounts):
                for col_idx, value in enumerate(account):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)  # Allow inline editing
                    table.setItem(row_idx, col_idx, item)

                    # Store the original value before editing
                    self.original_values[(row_idx, col_idx)] = str(value)

            # Connect signals for inline editing and delete key
            table.itemChanged.connect(self.confirm_inline_edit)
            table.keyPressEvent = self.handle_delete_key

            # Replace the dashboard content with the table
            self.app.central_widget.layout().removeWidget(self.app.dashboard)
            self.app.dashboard.deleteLater()
            self.app.dashboard = table
            self.app.central_widget.layout().addWidget(self.app.dashboard)

        except DatabaseError as e:
            QMessageBox.critical(self.app, "Database Error", str(e))

    def register_account(self):
        """Create a dialog for registering a new account."""
        dialog = QDialog(self.app)
        dialog.setWindowTitle("Register Account")

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        layout.addWidget(QLabel("Account Name:"))
        name_input = QLineEdit()
        layout.addWidget(name_input)

        layout.addWidget(QLabel("Account Type (debit/credit):"))
        type_input = QLineEdit()
        layout.addWidget(type_input)

        layout.addWidget(QLabel("Initial Balance:"))
        balance_input = QLineEdit()
        layout.addWidget(balance_input)

        register_button = QPushButton("Register Account")
        register_button.clicked.connect(lambda: self.create_account(name_input.text(), type_input.text(), balance_input.text(), dialog))
        layout.addWidget(register_button)

        dialog.exec()

    def create_account(self, name, account_type, balance, dialog):
        """Create a new account in the database."""
        if not name.strip() or not account_type.strip() or not balance.strip():
            QMessageBox.warning(self.app, "Input Error", "All fields are required.")
            return

        try:
            balance_value = float(balance)  # Ensure balance is a valid number
            self.db.execute(
                "INSERT INTO accounts (name, type, balance) VALUES (?, ?, ?)",
                (name, account_type.lower(), balance_value)
            )
            QMessageBox.information(self.app, "Success", "Account registered successfully.")
            dialog.accept()
            self.view_accounts()  # Refresh the dashboard

        except ValueError:
            QMessageBox.warning(self.app, "Input Error", "Balance must be a valid number.")
        except DatabaseError as e:
            QMessageBox.critical(self.app, "Database Error", str(e))

    def confirm_inline_edit(self, item):
        """Confirm inline editing before updating the database."""
        row = item.row()
        col = item.column()
        new_value = item.text()
        column_name = ["name", "type", "balance"][col]  # Map column index to database field

        # Get the original account name before editing
        original_name = self.original_values.get((row, 0), None)
        if not original_name:
            QMessageBox.critical(self.app, "Error", "Could not determine original account name.")
            return

        confirm = QMessageBox.question(
            self.app, "Confirm Edit",
            f"Do you want to update '{column_name}' to '{new_value}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                if col == 2:  # If updating balance, ensure it's a valid number
                    new_value = float(new_value)

                self.db.execute(
                    f"UPDATE accounts SET {column_name} = ? WHERE name = ?",
                    (new_value, original_name)
                )
                QMessageBox.information(self.app, "Success", "Account updated successfully.")

                # Update the stored original values
                if col == 0:  # If updating the name, update the stored key
                    self.original_values[(row, 0)] = new_value

            except ValueError:
                QMessageBox.warning(self.app, "Input Error", "Balance must be a valid number.")
            except DatabaseError as e:
                QMessageBox.critical(self.app, "Database Error", str(e))
        else:
            self.view_accounts()  # Revert changes if canceled

    def handle_delete_key(self, event: QKeyEvent):
        """Handle delete key press to confirm account deletion."""
        if event.key() == Qt.Key.Key_Delete:
            selected_row = self.app.dashboard.currentRow()
            if selected_row == -1:
                return

            account_name = self.app.dashboard.item(selected_row, 0).text()

            confirm = QMessageBox.question(
                self.app, "Confirm Deletion",
                f"Are you sure you want to delete '{account_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                self.execute_delete(account_name)

    def execute_delete(self, account_name):
        """Delete the selected account from the database."""
        try:
            self.db.execute("DELETE FROM accounts WHERE name = ?", (account_name,))
            QMessageBox.information(self.app, "Success", "Account deleted successfully.")
            self.view_accounts()  # Refresh the dashboard

        except DatabaseError as e:
            QMessageBox.critical(self.app, "Database Error", str(e))

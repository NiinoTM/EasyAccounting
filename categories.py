from PyQt6.QtWidgets import (
    QMenu, QMessageBox, QDialog, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from connection import DatabaseConnection, DatabaseError

class Categories:
    def __init__(self, app):
        self.db = DatabaseConnection()
        self.app = app
        self.original_values = {}  # Store original values before editing

    def create_categories_menu(self, parent_menu: QMenu):
        """Create the categories submenu."""
        categories_menu = parent_menu.addMenu("Categories")
        categories_menu.addAction("Register Category", self.register_category)
        categories_menu.addSeparator()
        categories_menu.addAction("View Categories", self.view_categories)
        categories_menu.addSeparator()

    def view_categories(self):
        """Fetch and display categories from the database in a table format."""
        try:
            categories = self.db.execute("SELECT name, description FROM account_categories").fetchall()

            if not categories:
                QMessageBox.information(self.app, "No Data", "No categories found in the database.")
                return

            # Create a table widget (Only 2 columns: Name, Description)
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Category Name", "Description"])
            table.setRowCount(len(categories))

            # Set column widths to fill the entire dashboard
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            # Populate the table with category data
            for row_idx, category in enumerate(categories):
                for col_idx, value in enumerate(category):
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

    def confirm_inline_edit(self, item):
        """Confirm inline editing before updating the database."""
        row = item.row()
        col = item.column()
        new_value = item.text()
        column_name = "name" if col == 0 else "description"

        # Get the original category name before editing
        original_name = self.original_values.get((row, 0), None)
        if not original_name:
            QMessageBox.critical(self.app, "Error", "Could not determine original category name.")
            return

        confirm = QMessageBox.question(
            self.app, "Confirm Edit",
            f"Do you want to update '{column_name}' to '{new_value}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.db.execute(
                    f"UPDATE account_categories SET {column_name} = ? WHERE name = ?",
                    (new_value, original_name)
                )
                QMessageBox.information(self.app, "Success", "Category updated successfully.")

                # Update the stored original values
                if col == 0:  # If updating the name, update the stored key
                    self.original_values[(row, 0)] = new_value

            except DatabaseError as e:
                QMessageBox.critical(self.app, "Database Error", str(e))
        else:
            self.view_categories()  # Revert changes if canceled

    def handle_delete_key(self, event: QKeyEvent):
        """Handle delete key press to confirm category deletion."""
        if event.key() == Qt.Key.Key_Delete:
            selected_row = self.app.dashboard.currentRow()
            if selected_row == -1:
                return

            category_name = self.app.dashboard.item(selected_row, 0).text()

            confirm = QMessageBox.question(
                self.app, "Confirm Deletion",
                f"Are you sure you want to delete '{category_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                self.execute_delete(category_name)

    def execute_delete(self, category_name):
        """Delete the selected category from the database."""
        try:
            self.db.execute("DELETE FROM account_categories WHERE name = ?", (category_name,))
            QMessageBox.information(self.app, "Success", "Category deleted successfully.")
            self.view_categories()  # Refresh the dashboard

        except DatabaseError as e:
            QMessageBox.critical(self.app, "Database Error", str(e))



    def register_category(self):
        """Create a dialog for registering a new category."""
        dialog = QDialog(self.app)
        dialog.setWindowTitle("Register Category")
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        layout.addWidget(QLabel("Category Name:"))
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        layout.addWidget(QLabel("Description (optional):"))
        description_input = QLineEdit()
        layout.addWidget(description_input)
        
        register_button = QPushButton("Register Category")
        register_button.clicked.connect(lambda: self.create_category(name_input.text(), description_input.text(), dialog))
        layout.addWidget(register_button)
        
        dialog.exec()

    def create_category(self, name, description, dialog):
        """Create a new category in the database and update the dashboard."""
        if not name.strip():
            QMessageBox.warning(self.app, "Input Error", "Category name cannot be empty.")
            return

        try:
            self.db.execute(
                "INSERT INTO account_categories (name, normalized_name, description) VALUES (?, ?, ?)",
                (name, name.lower(), description)
            )
            QMessageBox.information(self.app, "Success", "Category registered successfully.")
            dialog.accept()  # Close the dialog after successful registration

            # Automatically update the dashboard with the new category list
            self.view_categories()

        except DatabaseError as e:
            QMessageBox.critical(self.app, "Database Error", str(e))


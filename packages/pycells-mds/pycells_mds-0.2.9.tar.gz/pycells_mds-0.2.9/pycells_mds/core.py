# pycells.py

from .session import db
from .models import TableModel, ListModel
from pycells_mds.wrappers import TableWrapper
from pycells_mds.wrappers import ListWrapper
from pycells_mds.wrappers import CellWrapper
from pycells_mds.users import (
    register_user,
    login_user,
    safe_register_user
)





class PyCells:
    """
    Global facade for working with PyCells.
    The user sees only this class.
    """


    # =========================================================
    # USER API (PUBLIC)
    # =========================================================

    def register_user(self, username: str, password: str, email: str | None = None):
        """Registering a new user."""
        return register_user(username, password, email)

    def login(self, username: str, password: str) -> int | None:
        """Returns user_id upon successful authorization."""
        return login_user(username, password)

    def safe_register_user(self, username: str, password: str, email: str | None = None):
        """Registration only if there is no such user."""
        return safe_register_user(username, password, email)




    # ---------------------------------------------------------
    # TABLE OPERATIONS
    # ---------------------------------------------------------

    def ctable(self, name: str, user_id: int) -> TableWrapper:
        """
        Returns an existing table to the user
        or creates it if it does not exist.
        """
        table = (
            db.session.query(TableModel)
            .filter_by(name=name, author_id=user_id)
            .first()
        )

        if not table:
            table = TableModel(name=name, author_id=user_id)
            db.session.add(table)
            db.session.commit()

        return TableWrapper(table)

    def get_table(self, name: str, user_id: int) -> TableWrapper | None:
        """Get a table without creating it."""
        table = (
            db.session.query(TableModel)
            .filter_by(name=name, author_id=user_id)
            .first()
        )
        return TableWrapper(table) if table else None

    # ---------------------------------------------------------
    # LIST OPERATIONS
    # ---------------------------------------------------------

    def get_list(self, table_name: str, list_name: str, user_id: int) -> ListWrapper | None:
        """Get sheet by table and name."""
        tbl = self.get_table(table_name, user_id)
        if not tbl:
            return None

        lst = (
            db.session.query(ListModel)
            .filter_by(table_id=tbl.table_model.id, name=list_name)
            .first()
        )
        return ListWrapper(lst) if lst else None

    def get_or_create_list(self, table_name: str, list_name: str, user_id: int) -> ListWrapper:
        """Guaranteed to return the sheet."""
        tbl = self.ctable(table_name, user_id)
        return tbl.create_list(list_name)

    # ---------------------------------------------------------
    # CELL OPERATIONS (WRITE, READ, SELECT)
    # ---------------------------------------------------------

    def write(self, table: str, sheet: str, cell: str, value: str, user_id: int):
        """
        Universal entry:
            pc.write("Finance", "Main", "A1", "=5+10", user_id)
        """
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.write(cell, value)

    def read(self, table: str, sheet: str, cell: str, user_id: int):
        """
       Universal reading:
            pc.read("Finance", "Main", "A1", user_id)
        """
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.read(cell)

    def select(self, table: str, sheet: str, *cells, user_id: int):
        """
        Return a set of cells:
            pc.select("Finance", "Main", "A1", "B2", "C3", user_id=user_id)
        """
        lst = self.get_or_create_list(table, sheet, user_id)
        return {name: lst.read(name) for name in cells}

    # ---------------------------------------------------------
    # RE-CALC
    # ---------------------------------------------------------

    def recalc(self, table: str, sheet: str, user_id: int):
        """Recalculate all sheet cells."""
        lst = self.get_or_create_list(table, sheet, user_id)
        lst.recalc_all()
        return True
    


    # GROUP OPERATIONS
# ----------------------------------------------------------

    def create_group(self, table: str, sheet: str, name: str, cells: list[str], user_id: int, style: str = ""):
        """Creates a group on a sheet."""
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.add_group(name, cells, style)

    def update_group_style(self, table: str, sheet: str, name: str, style: str, user_id: int):
        """Updates the style of an existing group."""
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.update_group_style(name, style)

    def get_group_cells(self, table: str, sheet: str, name: str, user_id: int):
        """Returns a list of ORM cells that are included in the group."""
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.get_group_cells(name)

    def delete_group(self, table: str, sheet: str, name: str, user_id: int):
        """Deletes a group and clears the group_id of cells."""
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.delete_group(name)
    


    # Notes and Style
# ----------------------------------------------------------

    def set_style(self, table, sheet, cell, style, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.set_style(cell, style)

    def get_style(self, table, sheet, cell, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.get_style(cell)

    def set_note(self, table, sheet, cell, note, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.set_note(cell, note)

    def get_note(self, table, sheet, cell, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.get_note(cell)

    def clear_style(self, table, sheet, cell, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.clear_style(cell)

    def clear_note(self, table, sheet, cell, user_id):
        lst = self.get_or_create_list(table, sheet, user_id)
        return lst.clear_note(cell)
    

    def set_group_style(self, name, style):
        group = self.get_group(name)
        if not group:
            return None
        group.style = style
        db.session.commit()
        return group
    




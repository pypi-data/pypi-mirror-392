# tests/user_test.py

from pycells_mds import PyCells
from pycells_mds.session import init_db, db
from pycells_mds.users import register_user, login_user
from pycells_mds.models import TableModel, CellModel
from pycells_mds.managers import CursorManager

import re


pc = PyCells()


# ======================
#  Authentication
# ======================
def auth_flow():
    while True:
        choice = input("Choose action: [1] Login, [2] Register: ").strip()
        if choice not in ("1", "2"):
            print("Enter 1 or 2.")
            continue

        username = input("Username: ").strip()
        password = input("Password: ").strip()

        if choice == "2":
            email = input("Email (optional): ").strip() or None
            user = pc.register_user(username, password, email)
            print(f"User '{username}' registered.")
            return user.id

        user_id = pc.login(username, password)
        if not user_id:
            print("Invalid credentials, try again.")
            continue

        print(f"Welcome, {username}!")
        return user_id



# ======================
#  Table / Sheet
# ======================
def choose_table(user_id):
    # show tables
    tables = db.session.query(TableModel).filter_by(author_id=user_id).all()
    print("\nYour tables:")
    for t in tables:
        print(f"{t.id}: {t.name}")

    inp = input("Enter table ID or name of a new one: ").strip()

    if inp.isdigit():
        table = db.session.query(TableModel).filter_by(id=int(inp), author_id=user_id).first()
        if not table:
            print("No such table.")
            return choose_table(user_id)
    else:
        table = TableModel(name=inp, author_id=user_id)
        db.session.add(table)
        db.session.commit()
        print(f"Table '{inp}' created.")

    tbl = pc.ctable(table.name, user_id)

    # sheets
    lists = tbl.all_lists()
    if lists:
        print("\nSheets:")
        for i, lst in enumerate(lists, 1):
            print(f"{i}: {lst.model.name}")

        inp = input("Enter sheet number or press Enter for a new one: ").strip()
        if inp.isdigit() and 1 <= int(inp) <= len(lists):
            return lists[int(inp) - 1]
        else:
            return tbl.create_list("MainSheet")
    else:
        return tbl.create_list("MainSheet")



# ======================
#   Cursor mode
# ======================
def cursor_mode(sheet, user_id):
    while True:
        s = input("\nEnter cursor cells (A1,A2) or press Enter to skip: ").strip()
        if not s:
            return

        cells = [c.strip() for c in s.split(",") if c.strip()]
        if not cells:
            continue

        CursorManager.set_cursor(
            user_id=user_id,
            table_id=sheet.model.table_id,
            list_id=sheet.model.id,
            cells=cells
        )

        print("Cursor active:", cells)

        for cell in cells:
            val = input(f"{cell} = ").strip()
            sheet.write(cell, val)

        print("\nCurrent values:")
        for cell in cells:
            print(f"{cell} = {sheet.read(cell)}")



# ======================
#   Direct cell editing
# ======================
def direct_edit(sheet):
    while True:
        line = input("\nEnter: A1=10 or A1 10 or press Enter to exit: ").strip()
        if not line:
            return

        m = re.match(r"^([A-Z]+\d+)\s*=?\s*(.*)$", line)
        if not m:
            print("Invalid format.")
            continue

        addr, val = m.groups()
        sheet.write(addr, val)
        print(f"{addr} = {sheet.read(addr)}")



# ======================
#  Show cell IDs
# ======================
def show_cell_ids(sheet):
    print("\nCell IDs:")
    for name in ["A1", "A2", "A3", "B1", "C1"]:
        cell = (
            db.session.query(CellModel)
            .filter_by(
                table_id=sheet.model.table_id,
                list_id=sheet.model.id,
                name=name,
            )
            .first()
        )
        if cell:
            print(f"{name}: {cell.id}")



# ======================
#   MAIN
# ======================
def main():
    print("=== PyCells USER TEST ===\n")

    init_db({"engine": "sqlite", "path": "pycells_user_test.db"})
    print("Database connected.")

    user_id = auth_flow()
    sheet = choose_table(user_id)

    print(f"\nWorking in table '{sheet.model.table.name}', sheet '{sheet.model.name}'")

    cursor_mode(sheet, user_id)
    direct_edit(sheet)
    show_cell_ids(sheet)

    print("\nTEST COMPLETED.")



if __name__ == "__main__":
    main()

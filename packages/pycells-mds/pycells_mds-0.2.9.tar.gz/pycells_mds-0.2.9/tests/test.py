# test.py — full test of PyCells API
# --------------------------------------

from pycells_mds import init_db, PyCells
from pycells_mds.session import db

def main():

    print("\n=== 1. DATABASE INITIALIZATION ===")

    init_db({
        "engine": "sqlite",
        "path": "test_pycells.db"
    })

    pc = PyCells()
    print("Database connected.")


    print("\n=== 2. USER REGISTRATION ===")

    try:
        user = pc.register_user("zhandos", "0150", "z@cells.com")
    except Exception:
        print("User already exists. Logging in...")
        user_id = pc.login("zhandos", "0150")
    else:
        user_id = user.id

    print(f"User ID = {user_id}")


    print("\n=== 3. CREATING TABLE AND SHEET ===")

    tbl = pc.ctable("Finance", user_id)
    sheet = pc.get_or_create_list("Finance", "Main", user_id)

    print("Table: Finance")
    print("Sheet: Main")


    print("\n=== 4. WRITING CELLS ===")

    pc.write("Finance", "Main", "A1", "10", user_id)
    pc.write("Finance", "Main", "A2", "20", user_id)
    pc.write("Finance", "Main", "A3", "=A1+A2", user_id)

    print("A1=10, A2=20, A3 = A1+A2")


    print("\n=== 5. READING CELLS ===")

    print("A1:", pc.read("Finance", "Main", "A1", user_id))
    print("A2:", pc.read("Finance", "Main", "A2", user_id))
    print("A3:", pc.read("Finance", "Main", "A3", user_id))


    print("\n=== 6. FORMULA TEST ===")

    pc.write("Finance", "Main", "B1", "5", user_id)
    pc.write("Finance", "Main", "B2", "3", user_id)
    pc.write("Finance", "Main", "B3", "=B1^B2", user_id)  # 5^3 = 125

    print("B3 calculated:", pc.read("Finance", "Main", "B3", user_id))


    print("\n=== 7. FUNCTIONS WITH GLOBAL_NS ===")

    pc.write("Finance", "Main", "C1", "=SUM(A1:A3)", user_id)
    pc.write("Finance", "Main", "C2", "=IF(A1>5, 'OK', 'NO')", user_id)
    pc.write("Finance", "Main", "C3", "=UPPER('hello')", user_id)

    print("C1 SUM:", pc.read("Finance", "Main", "C1", user_id))
    print("C2 IF:", pc.read("Finance", "Main", "C2", user_id))
    print("C3 UPPER:", pc.read("Finance", "Main", "C3", user_id))


    print("\n=== 8. GROUPS ===")

    lst = pc.get_or_create_list("Finance", "Main", user_id)
    lst.add_group("Totals", ["A1", "A2", "A3"], style="color:red;")
    pc.recalc("Finance", "Main", user_id)
    db.session.flush()

    print("Group 'Totals' created")
    print("Its cells:", [c.name for c in lst.get_group_cells("Totals")])


    print("\n=== 9. SELECT ===")

    select_result = pc.select("Finance", "Main", "A1", "A3", "C1", user_id=user_id)
    print("Selection:", select_result)


    print("\n=== 10. RECALC ===")

    print("Changed A1 = 100")
    pc.write("Finance", "Main", "A1", "100", user_id)

    print("Recalculating...")
    pc.recalc("Finance", "Main", user_id)

    print("A3:", pc.read("Finance", "Main", "A3", user_id))
    print("C1:", pc.read("Finance", "Main", "C1", user_id))


    print("\n=== TEST COMPLETED ===\n")


if __name__ == "__main__":
    main()

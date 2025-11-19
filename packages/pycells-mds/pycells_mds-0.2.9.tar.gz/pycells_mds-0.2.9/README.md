[![PyCells](PyCells_mds.png)](https://pycells.com)



# pycells_mds

**Multidimensional Data Structures for Python**

[Homepage](https://pycells.com) • [Issues](https://pycells.com/issues)

---

## 🔍 Overview

PyCells is a library for working with spreadsheet-like data structures similar to Excel or Google Sheets, but fully implemented inside Python.

- It supports:

- tables and sheets

- formula-based cells

- ranges (A1:A10)

- functions (SUM, IF, UPPER, DATE, ETEXT, and more)

- cell groups

- automatic recalculation

- cursors (Redis + SQL)

- NumPy for range operations 

---

## 🛠 Installation

```bash
pip install pycells_mds
```
## Requirements
Python 3.9+

SQLAlchemy

NumPy

Redis (optional, used for CursorManager)

## 🚀 Quick Start
### 1) Initialize database

```bash
from pycells_mds.session import init_db

from pycells_mds.core import PyCells

db = init_db({
    "engine": "sqlite",
    "path": "my_cells.db"
})

pc = PyCells()

print("Database connected.")
```


### 2) Register user

```bash
user = pc.safe_register_user("user1", "pw123", "user1@example.com")

user_id = user.id
```

### 3) Create table and sheet

```bash
tbl = pc.ctable("Finance", user_id)

sheet = pc.get_or_create_list("Finance", "Main", user_id)
```

### 4) Work with cells

```bash
pc.write("Finance", "Main", "A1", "10", user_id)
pc.write("Finance", "Main", "A2", "20", user_id)
pc.write("Finance", "Main", "A3", "=A1+A2", user_id)

print(pc.read("Finance", "Main", "A3", user_id))
# → 30.0
```

## 🔢 Formulas
### Supported operators:

 (+), (-), (*), (/), (^)

### ranges: A1:A10

## Functions:

* SUM, MAX, MIN, AVERAGE
* ABS, ROUND, POWER
* INT, VALUE
* UPPER, LOWER, CONCAT, TEXTJOIN
* IF
* TODAY, NOW, DATE, YEAR, MONTH, DAY
* ETEXT — formatting numbers and dates
* np — NumPy access

## Examples:

```bash
pc.write("Finance", "Main", "B1", "=SUM(A1:A10)", user_id)

pc.write("Finance", "Main", "B2", "=A1^A2", user_id)
```

## 🎯 Groups

```bash
sheet = pc.get_or_create_list("Finance", "Main", user_id)

sheet.add_group("Totals", ["A1", "A2", "A3"], style="color:red;")

cells = sheet.get_group_cells("Totals")

print([c.name for c in cells])

# result → ['A1', 'A2', 'A3']
```

## Update style:

```bash
sheet.update_group_style("Totals", "background:yellow;")
```

## Delete group:

```bash
sheet.delete_group("Totals")
```


## 🖱 CursorManager (Redis + SQL)

```bash
from pycells_mds.managers import CursorManager

CursorManager.set_cursor(
    user_id=user_id,
    table_id=sheet.model.table_id,
    list_id=sheet.model.id,
    cells=["A1", "A2"]
)
```

# Get active cursor:

```
CursorManager.get_active(user_id)
```

## 🔄 Recalculation

```bash
pc.recalc("Finance", "Main", user_id)
```

## 📄 Select cells

```bash
cells = pc.select("Finance", "Main", ["A1", "A2", "A3"], user_id)
print(cells)
```

## 🌐 Website & Contacts
📌 Homepage: https://pycells.com
✉️ Email: zhandos.mambetali@gmail.com
☎️ WhatsApp: +7 701 457 7360

## 📜 License
MIT


---
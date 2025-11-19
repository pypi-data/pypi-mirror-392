# wrappers/list_wrapper.py

from .session import db
from .models import TableModel, ListModel, CellModel, GroupModel
import numpy as np
import datetime as dt
import re







def ETEXT(x, fmt: str = None):
    import re

    # --- If the string is with %, calculate it as a number ---
    if isinstance(x, str):
        x = x.strip()
        # Percent
        if x.endswith("%"):
            try:
                x = float(x[:-1]) / 100
            except:
                pass
        #Degree: "2^3"
        elif "^" in x:
            try:
                base, exp = x.split("^")
                x = float(base) ** float(exp)
            except:
                pass
        else:
            try:
                x = float(x)
            except:
                pass

    # --- If number ---
    if isinstance(x, (int, float)):
        if fmt == "0":          
            return f"{int(round(x))}"
        elif fmt == "0.0":      
            return f"{x:.1f}"
        elif fmt == "0.00":     
            return f"{x:.2f}"
        elif fmt == "0%":       
            return f"{round(x*100)}%"
        elif fmt == "0.0%":     
            return f"{x*100:.1f}%"
        elif fmt == "#,##0":    
            return f"{int(round(x)):,}"
        else:
            try:                
                return format(x, fmt)
            except:
                return str(x)

    # --- If date ---
    elif isinstance(x, (dt.date, dt.datetime)):
        mapping = {
            "dd.mm.yyyy": "%d.%m.%Y",
            "dd/mm/yyyy": "%d/%m/%Y",
            "yyyy-mm-dd": "%Y-%m-%d",
            "yyyy/mm/dd": "%Y/%m/%d",
        }
        py_fmt = mapping.get(fmt.lower())
        if py_fmt:
            return x.strftime(py_fmt)
        else:
            return str(x)

    # --- Elsе ---
    else:
        return str(x)





GLOBAL_NS = {
    # --- Arithmetic and Aggregates---
    "SUM": lambda lst: np.sum(lst) if isinstance(lst, (list, np.ndarray)) else lst,
    "MAX": lambda lst: np.max(lst) if isinstance(lst, (list, np.ndarray)) else lst,
    "MIN": lambda lst: np.min(lst) if isinstance(lst, (list, np.ndarray)) else lst,
    "AVERAGE": lambda lst: np.mean(lst) if isinstance(lst, (list, np.ndarray)) else lst,

    # --- Mathematics ---
    "ABS": np.abs,
    "ROUND": np.round,
    "POWER": lambda a, b: np.power(a, b),
    "PERCENT": lambda x: x / 100,
    "INT": lambda x: int(float(x)) if str(x).replace('.', '', 1).lstrip('-').isdigit() else 0,
    "VALUE": lambda x: float(x) if str(x).replace('.', '', 1).lstrip('-').isdigit() else 0.0,

    # --- Logics ---
    "IF": lambda cond, a, b: a if cond else b,

    # --- Text functions ---
    "CONCAT": lambda *args: "".join(str(a) for a in args if a is not None),
    "TEXTJOIN": lambda sep, *args: sep.join(str(a) for a in args if a is not None),
    "LEFT": lambda text, n=1: str(text)[:int(n)],
    "RIGHT": lambda text, n=1: str(text)[-int(n):],
    "LEN": lambda text: len(str(text)),
    "LOWER": lambda text: str(text).lower(),
    "UPPER": lambda text: str(text).upper(),
    "TRIM": lambda text: str(text).strip(),
    # --- TEXT: numbers and dates with format ---
    "TEXT": lambda x, fmt=None: (
        x.strftime(fmt) if isinstance(x, (dt.date, dt.datetime)) and fmt else
        format(x, fmt) if fmt and isinstance(x, (int, float)) else
        str(x)
    ),
    # --- Excel--TEXT() ---
    "ETEXT": ETEXT,

    # --- Dates and times---
    "TODAY": lambda: dt.date.today(),
    "NOW": lambda: dt.datetime.now(),
    "YEAR": lambda d: d.year if isinstance(d, (dt.date, dt.datetime)) else None,
    "MONTH": lambda d: d.month if isinstance(d, (dt.date, dt.datetime)) else None,
    "DAY": lambda d: d.day if isinstance(d, (dt.date, dt.datetime)) else None,
    "HOUR": lambda d: d.hour if isinstance(d, dt.datetime) else 0,
    "MINUTE": lambda d: d.minute if isinstance(d, dt.datetime) else 0,
    "SECOND": lambda d: d.second if isinstance(d, dt.datetime) else 0,
    "DATE": lambda y, m, d: dt.date(int(y), int(m), int(d)),
    "DATEDIF": lambda d1, d2: abs((d2 - d1).days) if all(isinstance(x, (dt.date, dt.datetime)) for x in (d1, d2)) else None,

    # --- Numpy for ranges ---
    "np": np,
}


def register_func(name, func):
    GLOBAL_NS[name.upper()] = func








class CellWrapper:
    """
    Single cell wrapper.
    Responsible for calculating formulas, reading/writing data,
    and executing cell level logic.
    """

    formula_pattern = re.compile(r"^=(.+)$")  #the formula starts with "="

    def __init__(self, cell_model: CellModel):
        self.model = cell_model
        self.session = db.session

    # ----------------------------------------------------------
    # READ AND WRITE
    # ----------------------------------------------------------

    def read_data(self):
        """Returns the text/formula written to a cell (cell.data)."""
        return self.model.data or ""

    def write_data(self, value: str):
        """Writes the new contents of a cell."""
        self.model.data = value
        self.session.commit()

    # ----------------------------------------------------------
    # CALCULATION
    # ----------------------------------------------------------

    def evaluate(self):
        """
       Calculates the value of a cell.
        If this is a formula, it parses and calculates.
        If it's plain text, it returns as is.
        """
        raw = self.read_data()

        # -----------------------------
        # 1) No formula, plain text
        # -----------------------------
        match = self.formula_pattern.match(raw)
        if not match:
            return raw or ""

        expr = match.group(1).strip()

        # -----------------------------
        # 2)IF THERE IS A FORMULA
        # -----------------------------
        return self._evaluate_formula(expr)

    # ----------------------------------------------------------
    # FORMULAS (minimal prototype)
    # ----------------------------------------------------------

    def _evaluate_formula(self, expr: str):
        import string

        # --- helper functions for ranges ---
        def col_to_index(col: str) -> int:
            # A -> 1, Z -> 26, AA -> 27
            col = col.upper()
            idx = 0
            for ch in col:
                if ch in string.ascii_uppercase:
                    idx = idx * 26 + (ord(ch) - ord("A") + 1)
            return idx

        def index_to_col(index: int) -> str:
            # 1 -> A, 27 -> AA
            result = ""
            while index > 0:
                index, rem = divmod(index - 1, 26)
                result = chr(rem + ord("A")) + result
            return result

        def split_cell(cell_name: str):
            m = re.match(r"^([A-Za-z]+)(\d+)$", cell_name)
            if not m:
                raise ValueError(f"Invalid cell name: {cell_name}")
            return m.group(1).upper(), int(m.group(2))

        def expand_range(a: str, b: str):
            #returns a list of cell names from a to b (incl.)
            col_a, row_a = split_cell(a)
            col_b, row_b = split_cell(b)

            c1 = col_to_index(col_a)
            c2 = col_to_index(col_b)
            r1 = row_a
            r2 = row_b

            cols = range(min(c1, c2), max(c1, c2) + 1)
            rows = range(min(r1, r2), max(r1, r2) + 1)

            cells = []
            for ci in cols:
                for ri in rows:
                    cells.append(f"{index_to_col(ci)}{ri}")
            return cells

        # --- 1) Processing ranges of the form A1:A3---
        # Find all occurrences of ranges and replace them with lists of values
        range_pattern = re.compile(r"([A-Za-z]+[0-9]+):([A-Za-z]+[0-9]+)")
        # make multiple passes to catch nested/multiple ranges
        while True:
            m = range_pattern.search(expr)
            if not m:
                break
            a, b = m.group(1), m.group(2)
            names = expand_range(a, b)

            vals = []
            for name in names:
                # find a cell, calculate it recursively
                cell = (
                    self.session.query(CellModel)
                    .filter_by(table_id=self.model.table_id,
                                list_id=self.model.list_id,
                                name=name)
                    .first()
                )
                if not cell:
                    vals.append(0)
                    continue
                wrap = CellWrapper(cell)
                v = wrap.evaluate()
                # attempt to cast to a number, otherwise leave it as a string
                try:
                    nv = float(v)
                except Exception:
                    #if the string is like a string (with quotes)
                    nv = v
                vals.append(nv)

            # We substitute the Python leaf into the expression:
            # strings should be reprs, numbers should be as is
            py_items = []
            for v in vals:
                if isinstance(v, (int, float)):
                    py_items.append(str(v))
                else:
                    #escape quotes correctly
                    py_items.append(repr(str(v)))
            list_literal = "[" + ",".join(py_items) + "]"

            # replace the first occurrence of the range with list_literal
            expr = expr[:m.start()] + list_literal + expr[m.end():]

        # --- 2) Now let's process simple links like A1, B2---
        tokens = re.findall(r"[A-Za-z]+[0-9]+", expr)

        # To avoid re-processing ranges and already substituted lists,
        # use a dictionary, but do the replacement via regex with boundaries.
        values = {}

        for token in sorted(set(tokens), key=lambda s: -len(s)):
            # we skip cases where the token is already inside a list literal (for example [1,2,A1])
            if re.search(r"\[" + re.escape(token) + r"\]", expr):
                # already processed inside the list
                continue

            cell = (
                self.session.query(CellModel)
                .filter_by(table_id=self.model.table_id,
                            list_id=self.model.list_id,
                            name=token)
                .first()
            )

            if not cell:
                values[token] = 0
                continue

            wrap = CellWrapper(cell)
            val = wrap.evaluate()

            # if it’s a number, we’ll convert it to a float, otherwise we’ll leave it as a string
            try:
                numeric_val = float(val)
                values[token] = numeric_val
            except Exception:
                # string values ​​must be properly escaped when substituting
                values[token] = repr(str(val))

        #We carefully replace tokens (with boundaries) with their values
        expr_eval = expr
        for k, v in values.items():
            # if v is a number (int/float), insert it as is; if the string is v already repr
            if isinstance(v, (int, float)):
                repl = str(v)
            else:
                repl = v
            expr_eval = re.sub(rf"\b{re.escape(k)}\b", repl, expr_eval)

        # --- 3) Replace the operator ^ with ** (Excel power) ---
        # but do not change inside the lines (simple approach - if there are quotes, leave the risk)
        expr_eval = expr_eval.replace("^", "**")

        # --- 4) Eval in a secure environment with GLOBAL_NS ---
        try:
            result = eval(expr_eval, {"__builtins__": {}}, GLOBAL_NS)
        except Exception:
            result = "#ERROR"

        return result







class ListWrapper:
    """
    Logical wrapper of the sheet.
    Works with models, recalculation, functions, reading/writing cells.
    """

    def __init__(self, list_model: ListModel):
        self.model = list_model
        self.session = db.session   #single session from session.py

    # ------------------------------------------
    # BASIC LIST OPERATIONS
    # ------------------------------------------

    def get_cell(self, name: str) -> CellModel | None:
        """Возвращает ORM CellModel по имени ячейки."""
        return (
            self.session.query(CellModel)
            .filter_by(list_id=self.model.id, name=name)
            .first()
        )

    def read(self, name: str):
        """
       Returns the current value of a cell.
        If there is a formula, it will return the already calculated value.
        If value is empty, the empty string.
        """
        cell = self.get_cell(name)
        if not cell:
            return ""

        return cell.value if cell.value is not None else ""

    def write(self, name: str, value: str):
        cell = self.get_cell(name)

        if not cell:
            cell = CellModel(
                list_id=self.model.id,
                table_id=self.model.table_id,
                name=name,
                data=value,
            )
            self.session.add(cell)
        else:
            cell.data = value

        # === add automatic recalculation ===
        wrapper = CellWrapper(cell)
        try:
            cell.value = wrapper.evaluate()
        except:
            cell.value = "#ERROR"

        self.session.commit()
        return cell


    # ------------------------------------------
    # CALCULATION
    # ------------------------------------------

    def evaluate_cell(self, name: str):
        """Пересчитать конкретную ячейку."""
        cell = self.get_cell(name)
        if not cell:
            return None

        wrapper = CellWrapper(cell)
        try:
            result = wrapper.evaluate()
            cell.value = result
            self.session.commit()
            return result

        except Exception:
            cell.value = "#ERROR"
            self.session.commit()
            return "#ERROR"

    def recalc_all(self):
        """
        Recalculate all sheet cells.
        Complete replacement of the old recalc_all_safe().
        The logic now lies HERE, and not in the model.
        """
        for cell in self.model.cells:
            wrapper = CellWrapper(cell)
            try:
                value = wrapper.evaluate()
                cell.value = value
            except Exception:
                cell.value = "#ERROR"

        self.session.commit()

    # ------------------------------------------
    # СТРАТЕГИЧЕСКИЕ ОПЕРАЦИИ
    # ------------------------------------------

    def get_all_cells(self):
        """Return all sheet cells (ORM objects)."""
        return self.model.cells

    def delete_cell(self, name: str):
        """Delete cell by name."""
        cell = self.get_cell(name)
        if cell:
            self.session.delete(cell)
            self.session.commit()

    def clear(self):
        """Delete all worksheet cells."""
        for cell in self.model.cells:
            self.session.delete(cell)
        self.session.commit()


    def add_group(self, name: str, cell_names: list[str], style: str = ""):
        """Creates a group and adds the specified cells to it."""

        # create a group
        group = GroupModel(
            list_id=self.model.id,
            name=name,
            style=style,
        )
        db.session.add(group)
        db.session.commit()

        # linking cells to a group
        cells = (
            db.session.query(CellModel)
            .filter(
                CellModel.list_id == self.model.id,
                CellModel.name.in_(cell_names)
            )
            .all()
        )

        for cell in cells:
            cell.group_id = group.id

        db.session.commit()
        return group
    


    def get_group(self, name: str):
        return (
            db.session.query(GroupModel)
            .filter_by(list_id=self.model.id, name=name)
            .first()
        )
    


    def update_group_style(self, name: str, style: str):
        group = self.get_group(name)
        if not group:
            return None

        group.style = style
        db.session.commit()
        return group
    


    def get_group_cells(self, name: str):
        group = self.get_group(name)
        if not group:
            return []

        return group.cells




    def delete_group(self, name: str):
        group = self.get_group(name)
        if not group:
            return None

        # clean bindings
        for cell in group.cells:
            cell.group_id = None

        db.delete(group)
        db.session.commit()
        return True
    


        group.style = style
        db.session.commit()

        for cell in group.cells:
            # if the cell does not have its own style
            if not cell.style:
                cell.style = style

        db.session.commit()
        return group
    


    def get_style(self, name: str) -> str:
        cell = self.get_cell(name)
        return cell.style if cell else ""
    


    def set_style(self, name: str, style: str):
        cell = self.get_cell(name)
        if not cell:
            return None
        cell.style = style
        self.session.commit()
        return cell
    


    def get_note(self, name: str) -> str:
        cell = self.get_cell(name)
        return cell.note if cell else ""
    


    def set_note(self, name: str, note: str):
        cell = self.get_cell(name)
        if not cell:
            return None
        cell.note = note
        self.session.commit()
        return cell
    


    def clear_style(self, name: str):
        cell = self.get_cell(name)
        if cell:
            cell.style = ""
            self.session.commit()
            

    def clear_note(self, name: str):
        cell = self.get_cell(name)
        if cell:
            cell.note = None
            self.session.commit()















class TableWrapper:
    """
    Table wrapper (like Excel workbook: Book → Sheets).
    Manages sheets, the active sheet, and basic operations.
    """

    def __init__(self, table_model: TableModel):
        self.model = table_model
        self.session = db.session

    # ----------------------------------------------------------
    # RECEIVING SHEETS
    # ----------------------------------------------------------

    def get_list(self, name: str) -> ListWrapper | None:
        """Получить существующий лист по имени."""
        lst = (
            self.session.query(ListModel)
            .filter_by(table_id=self.model.id, name=name)
            .first()
        )
        return ListWrapper(lst) if lst else None

    def all_lists(self):
        """Вернуть все листы таблицы."""
        return [ListWrapper(lst) for lst in self.model.lists]

    # ----------------------------------------------------------
    # CREATING A SHEET
    # ----------------------------------------------------------

    def create_list(self, name: str, password: str | None = None):
        """Creates a new sheet in the table."""
        exists = (
            self.session.query(ListModel)
            .filter_by(table_id=self.model.id, name=name)
            .first()
        )

        if exists:
            return ListWrapper(exists)

        lst = ListModel(
            table_id=self.model.id,
            name=name,
            password=password,
        )

        self.session.add(lst)
        self.session.commit()

        return ListWrapper(lst)

    # ----------------------------------------------------------
    # REMOVING A SHEET
    # ----------------------------------------------------------

    def delete_list(self, name: str):
        """Deletes a sheet by name."""
        lst = (
            self.session.query(ListModel)
            .filter_by(table_id=self.model.id, name=name)
            .first()
        )

        if lst:
            self.session.delete(lst)
            self.session.commit()

    # ----------------------------------------------------------
    # ACTIVE SHEET
    # ----------------------------------------------------------

    def set_active_list(self, name: str):
        """Assigns the active sheet."""
        lst = (
            self.session.query(ListModel)
            .filter_by(table_id=self.model.id, name=name)
            .first()
        )

        if not lst:
            return None

        self.model.active_list_id = lst.id
        self.session.commit()

        return ListWrapper(lst)

    def get_active_list(self) -> ListWrapper | None:
        """Returns the active sheet."""
        if not self.model.active_list_id:
            return None

        lst = self.session.query(ListModel).get(self.model.active_list_id)
        return ListWrapper(lst) if lst else None

    # ----------------------------------------------------------
    # UTILITIES / METADATA
    # ----------------------------------------------------------

    def rename(self, new_name: str):
        """Rename table."""
        self.model.name = new_name
        self.session.commit()

    def delete(self):
        """Delete table with all sheets."""
        self.session.delete(self.model)
        self.session.commit()




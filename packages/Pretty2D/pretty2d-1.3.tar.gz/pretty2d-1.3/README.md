# Pretty2D

A lightweight and easy-to-use Python library for **pretty-printing 2D tabular data** with multiple border styles, including default ASCII, tabular Unicode, rounded, double-line, and borderless modes.

Perfect for CLIs, logs, debugging, table previews, and formatted console output.

---

## 🔧 Installation

```bash
pip install Pretty2D
```

---

## 🚀 Quick Start

```python
from pretty2d import formatter, border

data = [
    ["Name", "Age", "City"],
    ["Alice", "23", "London"],
    ["Bob", "31", "Paris"],
]

print(formatter.format(data, True, border.Border.TABULAR))
```

---

## 🖼 Output Examples

### **Default Border**

```
+-------+-----+--------+
| Name  | Age | City   |
+-------+-----+--------+
| Alice | 23  | London |
| Bob   | 31  | Paris  |
+-------+-----+--------+
```

### **Tabular**

```
┌───────┬─────┬────────┐
│ Name  │ Age │ City   │
├───────┼─────┼────────┤
│ Alice │ 23  │ London │
│ Bob   │ 31  │ Paris  │
└───────┴─────┴────────┘
```

### **Rounded**

```
╭───────┬─────┬────────╮
│ Name  │ Age │ City   │
├───────┼─────┼────────┤
│ Alice │ 23  │ London │
│ Bob   │ 31  │ Paris  │
╰───────┴─────┴────────╯
```

### **Double Borders**

```
╔═══════╦═════╦════════╗
║ Name  ║ Age ║ City   ║
╠═══════╬═════╬════════╣
║ Alice ║ 23  ║ London ║
║ Bob   ║ 31  ║ Paris  ║
╚═══════╩═════╩════════╝
```

### **No Border**

```
| Name  | Age | City   |
| Alice | 23  | London |
| Bob   | 31  | Paris  |
```

> **Note:** `NO_BORDER` cannot be used with headers.

---

## 📦 Border Options

```python
class Border(Enum):
    DEFAULT = 1
    TABULAR = 2
    TABULAR_ROUNDED = 3
    TABULAR_DOUBLE = 4
    NO_BORDER = 5
```

---

## 🧠 How It Works

The main function you call is:

```python
format(data: list[list[str]], hasHeader: bool, border: Border)
```

### ✔ Auto-aligns columns  
### ✔ Detects max width for each column  
### ✔ Supports uneven row lengths  
### ✔ Handles header separators  
### ✔ Multiple border styles  

Example:

```python
from pretty2d import format, Border

data = [
    ["Product", "Price"],
    ["Keyboard", "$49"],
    ["Mouse", "$19"],
]

print(format(data, hasHeader=True, border=Border.DEFAULT))
```

---

## ❗ Exceptions

| Condition | Raises |
|----------|--------|
| Using `NO_BORDER` with `hasHeader=True` | `TypeError` |

---

## 📚 API Reference

### **format(data, hasHeader, border)**

Formats a 2D list of strings into a pretty-printed table.

**Parameters:**
- `data` — list of rows, each row a list of strings  
- `hasHeader` — whether the first row is a header  
- `border` — a value from the `Border` enum  

**Returns:**  
A formatted string.

---

## 📁 Project Structure

```
pretty2d/
 ├── __init__.py
 ├── formatter.py
 └── border.py
```

---

## 🔓 License

This project is licensed under the MIT License.  
See the `LICENSE` file for details.

---

## ⭐ Contribute

Feel free to open issues or pull requests on GitHub!

---

Enjoy clean ASCII/Unicode tables with **Pretty2D** 🎉

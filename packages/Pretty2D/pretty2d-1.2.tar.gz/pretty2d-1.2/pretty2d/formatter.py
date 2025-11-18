from .border import Border

class Formatter:
    def __format_default(self, data, width, h):
        header = h
        border = ""
        for w in width:
            border += ("+" + ("-" * (w +2)))
        border += "+"
        text = border + "\n"
        for row in data:
            i = 0
            for word in row:
                text += f"| {word} " + (" " * (width[i] - len(word)))
                i += 1
            text += "|\n"
            if header:
                header = False
                text += f"{border}\n"
        text += border
        return text
        
    def __format_tabular(self, data, width, h):
        border_top = "┌"
        border_mid = "├"
        border_bot = "└"
        i = 0
        for w in width:
            space = ("─" * (w + 2))
            border_top += space
            border_mid += space
            border_bot += space
            if i < len(width) - 1:
                border_top += "┬"
                border_mid += "┼"
                border_bot += "┴"
            i += 1
        border_top += "┐"
        border_mid += "┤"
        border_bot += "┘"
        text = border_top + "\n"
        for row in data:
            i = 0
            for word in row:
                text += f"│ {word} " + (" " * (width[i] - len(word)))
                i += 1
            text += "│\n"
            if h:
                h = False
                text += f"{border_mid}\n"
        text += border_bot
        return text
        
    def __format_tabular_rounded(self, data, width, h):
        border_top = "╭"
        border_mid = "├"
        border_bot = "╰"
        i = 0
        for w in width:
            space = ("─" * (w + 2))
            border_top += space
            border_mid += space
            border_bot += space
            if i < len(width) - 1:
                border_top += "┬"
                border_mid += "┼"
                border_bot += "┴"
            i += 1
        border_top += "╮"
        border_mid += "┤"
        border_bot += "╯"
        text = border_top + "\n"
        for row in data:
            i = 0
            for word in row:
                text += f"│ {word} " + (" " * (width[i] - len(word)))
                i += 1
            text += "│\n"
            if h:
                h = False
                text += f"{border_mid}\n"
        text += border_bot
        return text
    
    def __format_tabular_double(self, data, width, h):
        border_top = "╔"
        border_mid = "╠"
        border_bot = "╚"
        i = 0
        for w in width:
            space = ("═" * (w + 2))
            border_top += space
            border_mid += space
            border_bot += space
            if i < len(width) - 1:
                border_top += "╦"
                border_mid += "╬"
                border_bot += "╩"
            i += 1
        border_top += "╗"
        border_mid += "╣"
        border_bot += "╝"
        text = border_top + "\n"
        for row in data:
            i = 0
            for word in row:
                text += f"║ {word} " + (" " * (width[i] - len(word)))
                i += 1
            text += "║\n"
            if h:
                h = False
                text += f"{border_mid}\n"
        text += border_bot
        return text
        
    def __format_no_border(self, data, width):
        text = ""
        for row in data:
            i = 0
            for word in row:
                text += f"| {word} " + (" " * (width[i] - len(word))) + "|"
                i += 1
            text += "\n"
        return text

def format(data, hasHeader, border: Border = Border.DEFAULT):
    max_cols = 0
    for row in data:
        if len(row) > max_cols:
            max_cols = len(row)
    new_data = []
    for row in data:
        for i in range(max_cols - len(row)):
            row.append(" ")
        new_data.append(row)
    matrix = [row for row in zip(*new_data)]
    max_width = []
    for row in matrix:
        m = 0
        for word in row:
            if (len(word) > m):
                m = len(word)
        max_width.append(m)
    f = Formatter()
    match border:
        case Border.DEFAULT:
            return f._Formatter__format_default(data, max_width, hasHeader)
        case Border.TABULAR:
            return f._Formatter__format_tabular(data, max_width, hasHeader)
        case Border.TABULAR_ROUNDED:
            return f._Formatter__format_tabular_rounded(data, max_width, hasHeader)
        case Border.TABULAR_DOUBLE:
            return f._Formatter__format_tabular_double(data, max_width, hasHeader)
        case Border.NO_BORDER:
            if hasHeader:
                raise TypeError("In No Border Mode, Data Cannot Have Header")
            else:
                return f._Formatter__format_no_border(data, max_width)

def test():
    data = [
        ["Name", "Age", "City"],
        ["Alice", "23", "London"],
        ["Bob", "31", "Paris"],
    ]

    print("\n=== DEFAULT ===")
    print(format(data, True, Border.DEFAULT))

    print("\n=== TABULAR ===")
    print(format(data, True, Border.TABULAR))

    print("\n=== TABULAR_ROUNDED ===")
    print(format(data, True, Border.TABULAR_ROUNDED))

    print("\n=== TABULAR_DOUBLE ===")
    print(format(data, True, Border.TABULAR_DOUBLE))

    print("\n=== NO_BORDER ===")
    print(format(data, False, Border.NO_BORDER))

if __name__ == "__main__":
    test()

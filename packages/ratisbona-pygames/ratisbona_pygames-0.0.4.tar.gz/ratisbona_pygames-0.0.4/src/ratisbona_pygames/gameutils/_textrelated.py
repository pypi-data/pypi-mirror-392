from dataclasses import dataclass
from typing import Any, Union, Tuple, List

from pygame import Surface, Vector2
from pygame.font import Font


@dataclass
class TableCell:
    value: str


@dataclass
class TableColumn:
    width: int


@dataclass
class TableRow:
    height: int


@dataclass
class SimpleTable:
    cells: List[List[TableCell]]

    def __init__(self, font: Font):
        self.cells = []
        self._default_font = font
        self.columns = []
        self.rows = []

    def _ensure_size(self, rows: int, columns: int):

        while len(self.columns) <= columns:
            self.columns.append(TableColumn(0))

        while len(self.rows) <= rows:
            self.rows.append(TableRow(0))

        while len(self.cells) <= rows:
            self.cells.append([])

        for row in self.cells:
            while len(row) <= columns:
                row.append(TableCell(""))

    def set_value(self, row: int, column: int, value: str):
        self._ensure_size(row, column)
        self.cells[row][column].value = value
        self._determine_column_widths()
        self._determine_row_heights()

    def _determine_cell_width(self, cell: TableCell) -> int:
        return self._default_font.size(cell.value)[0]

    def _determine_column_widths(self):
        for row in self.rows:
            for i, cell in enumerate(row):
                self.columns[i].width = max(
                    self.columns[i].width, self._determine_cell_width(cell)
                )

    def _determine_cell_height(self, cell: TableCell) -> int:
        return self._default_font.get_linesize()

    def _determine_row_heights(self):
        for row in self.rows:
            row.height = max(self._determine_cell_height(cell) for cell in row)

    def render(self, surface: Surface, pos: Tuple[int, int]):
        table_pos = Vector2(pos)
        running_sum_height = 0
        for row, cell_row in zip(self.rows, self.cells):
            running_sum_width = 0
            for column, cell in zip(self.columns, cell_row):
                cellpos = table_pos + Vector2(running_sum_width, running_sum_height)
                surface.blit(
                    self._default_font.render(cell.value, True, "black"), cellpos
                )
                running_sum_width += column.width
            running_sum_height += row.height


from __future__ import annotations
from collections.abc import Iterable, Iterator
from sheet_stream.type_utils.list import (
    ArrayString, ListString, ListColumnBody,
    HeadCell, HeadValues,
)
from sheet_stream.erros import (
    RowLargeError, ListTableLargeError, RowShortError, ListTableShortError,
)
from sheet_stream.type_utils.enums import ColumnsTable
import pandas as pd
import os
from soup_files import File


class TableRow(ArrayString):
    """
        Lista de strings nomeada para representar os dados de uma linha de tabela.
    """

    def __init__(self, numeric_str: HeadCell | str, col_body: list[str]):
        super().__init__(col_body)
        if isinstance(numeric_str, str):
            numeric_str = HeadCell(numeric_str)
        self.row_index: HeadCell = numeric_str


class BaseDict(dict):

    def __init__(self, body_list: list[ListColumnBody] = None):
        # Conjunto chave/valor
        local_args: dict[HeadCell, ListColumnBody] = {}
        # Lista de chaves/ list[str]
        self.__header: HeadValues = HeadValues()
        if body_list is None:
            body_list = []
        if len(body_list) == 0:
            super().__init__(local_args)
        else:
            # Atribuir uma lista de strings para cada chave.
            max_num: int = len(body_list[0])
            col: ListColumnBody
            for col in body_list:
                current_num_list: int = len(col)
                if current_num_list > max_num:
                    raise ListTableLargeError(
                        f'Coluna {col.col_name} excedeu o tamanho máximo da tabela -> {max_num}'
                    )
                elif current_num_list < max_num:
                    raise ListTableShortError(
                        f'Coluna {col.col_name} é menor que o tamanho minimo da tabela -> {max_num}'
                    )
                local_args[col.col_name] = col
                self.__header.add_item(col.col_name)
            super().__init__(local_args)

    @property
    def header(self) -> HeadValues:
        __items = HeadValues()
        for k in self.keys():
            __items.add_item(k)
        return __items

    @property
    def length(self) -> int:
        if self.header.length == 0:
            return 0
        return self.get(self.header.first).length

    @property
    def first(self) -> ListColumnBody:
        return self.get(self.header.first)

    @property
    def last(self) -> ListColumnBody:
        return self.get(self.header.last)

    def keys(self) -> ListString:
        return ListString(list(super().keys()))

    def values(self) -> list[ListColumnBody]:
        return list(super().values())

    def get(self, col: HeadCell | str) -> ListColumnBody:
        return self[col]

    def contains(self, value: str, *, case: bool = True, iqual: bool = False) -> bool:
        cols: HeadValues = self.header
        element: ListColumnBody
        for c in cols:
            element = self[c]
            if element.contains(value, case=case, iqual=iqual):
                return True
        return False

    def set_column(self, col: ListColumnBody):
        """
        Adiciona ou atualiza uma coluna de tabela.
        """
        if self.length > 0:
            if col.length > self.length:
                raise ListTableLargeError(
                    f'Coluna {col.col_name} excedeu o tamanho máximo da tabela'
                )
            elif col.length < self.length:
                raise ListTableShortError(
                    f'Coluna {col.col_name} é menor que o tamanho minimo da tabela'
                )
        # Cria ou atualiza
        self[col.col_name] = col

    def get_column(self, col_name: str | HeadCell) -> ListColumnBody:
        if isinstance(col_name, str):
            col_name = HeadCell(col_name)
        return self[col_name]

    def get_row(self, idx: int) -> TableRow:
        _row: ArrayString = ArrayString()
        _cols: HeadValues = self.header
        c: HeadCell
        for c in _cols:
            _row.append(self.get(c).get(idx))
        return TableRow(f'{idx}', _row)

    def add_row(self, row: TableRow):
        _size_row: int = row.length
        _size_tb: int = self.length
        _cols = self.header
        if _size_row > _size_tb:
            raise RowLargeError()
        elif _size_row < _size_tb:
            raise RowShortError()

        for n, line in enumerate(row):
            self[_cols[n]].append(line)

    def update_row(self, row: TableRow):
        _num_row = row.length
        _num_tb = self.length
        _cols = self.header
        if _num_row > _num_tb:
            raise RowLargeError()
        elif _num_row < _num_tb:
            raise RowShortError()

        update_idx: int = int(row.row_index)
        for n, line in enumerate(row):
            self[_cols[n]][update_idx] = line


class TableTextKeyWord(BaseDict):
    """
    Dicionário com strings que apontam para listas de strings.
    """

    def __init__(self, body_list: list[ListColumnBody] = None):
        super().__init__(body_list)

    def iter_rows(self, reverse: bool = False) -> IterRows:
        return IterRows(self, reverse)

    def __iter__(self):
        return self.iter_rows()


class IterRows(Iterator):

    def __init__(self, table: TableTextKeyWord, reverse: bool = False):
        self.table: TableTextKeyWord = table
        self.reverse: bool = reverse

        if self.reverse:
            self.__current_idx: int = -1
            self.__max_idx: int = -self.table.length-1
        else:
            self.__current_idx: int = 0
            self.__max_idx: int = self.table.length

    def has_next(self) -> bool:
        if self.reverse:
            if self.__current_idx <= self.__max_idx:
                return False
        else:
            if self.__current_idx >= self.__max_idx:
                return False
        return True

    def __next__(self) -> TableRow:
        if not self.has_next():
            raise StopIteration()
        idx_value = self.__current_idx
        if self.reverse:
            self.__current_idx -= 1
        else:
            self.__current_idx += 1
        return self.table.get_row(idx_value)


class TableDocuments(TableTextKeyWord):

    default_columns: list[ListColumnBody] = [
        ListColumnBody(ColumnsTable.KEY, ListString([])),
        ListColumnBody(ColumnsTable.NUM_PAGE, ListString([])),
        ListColumnBody(ColumnsTable.NUM_LINE, ListString([])),
        ListColumnBody(ColumnsTable.TEXT, ListString([])),
        ListColumnBody(ColumnsTable.FILE_NAME, ListString([])),
        ListColumnBody(ColumnsTable.FILETYPE, ListString([])),
        ListColumnBody(ColumnsTable.FILE_PATH, ListString([])),
        ListColumnBody(ColumnsTable.DIR, ListString([])),
    ]

    def __init__(self, body_list: list[ListColumnBody]):
        super().__init__(body_list)

    @property
    def columns(self) -> HeadValues:
        return self.header

    def to_data(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self)

    @classmethod
    def create_void_dict(cls) -> TableDocuments:
        _default: list[ListColumnBody] = [
            ListColumnBody(ColumnsTable.KEY, ListString([])),
            ListColumnBody(ColumnsTable.NUM_PAGE, ListString([])),
            ListColumnBody(ColumnsTable.NUM_LINE, ListString([])),
            ListColumnBody(ColumnsTable.TEXT, ListString([])),
            ListColumnBody(ColumnsTable.FILE_NAME, ListString([])),
            ListColumnBody(ColumnsTable.FILETYPE, ListString([])),
            ListColumnBody(ColumnsTable.FILE_PATH, ListString([])),
            ListColumnBody(ColumnsTable.DIR, ListString([])),
        ]
        return cls(_default)

    @classmethod
    def create_void_df(cls) -> pd.DataFrame:
        return pd.DataFrame.from_dict(cls.create_void_dict())

    @classmethod
    def create_from_values(
                cls,
                values: list[str], *,
                page_num: str = 'nan',
                file_path: str = 'nan',
                dir_path: str = 'nan',
                file_type: str = 'nan',
                remove_empty_txt: bool = True,
            ) -> TableDocuments:
        if remove_empty_txt:
            new_list = []
            for i in values:
                if (i == '') or (i is None):
                    continue
                new_list.append(i)
            values = new_list

        max_num = len(values)
        if max_num < 1:
            return cls.create_void_dict()

        _items = [
            ListColumnBody(
                ColumnsTable.KEY, ListString([f'{x}' for x in range(0, max_num)])
            ),
            ListColumnBody(
                ColumnsTable.NUM_PAGE, ListString([page_num] * max_num)
            ),
            ListColumnBody(
                ColumnsTable.NUM_LINE, ListString([f'{x+1}' for x in range(0, max_num)])
            ),
            ListColumnBody(
                ColumnsTable.TEXT, ListString(values)
            ),
            ListColumnBody(
                ColumnsTable.FILE_NAME, ListString([os.path.basename(file_path)] * max_num)
            ),
            ListColumnBody(
                ColumnsTable.FILETYPE, ListString([file_type] * max_num)
            ),
            ListColumnBody(
                ColumnsTable.FILE_PATH, ListString([file_path] * max_num)
            ),
            ListColumnBody(
                ColumnsTable.DIR, ListString([dir_path] * max_num)
            ),
        ]
        return cls(_items)

    @classmethod
    def create_from_file_text(cls, file: File) -> TableDocuments:
        if not isinstance(file, File):
            return cls.create_void_dict()

        try:
            with open(file.absolute(), 'rt') as f:
                lines = ListString(f.readlines())
        except Exception as e:
            print(e)
            return cls.create_void_dict()
        else:
            return cls.create_from_values(
                lines,
                file_type=file.extension(),
                file_path=file.absolute(),
                dir_path=file.dirname(),
            )


def concat_table_documents(list_map: list[TableDocuments]) -> TableDocuments:
    if len(list_map) < 1:
        return TableDocuments.create_void_dict()
    _columns: HeadValues = list_map[0].columns
    list_values: list[ListColumnBody] = []
    text_table: TableDocuments
    col: ListColumnBody
    i: HeadCell

    for i in _columns:
        list_values.append(
            ListColumnBody(i, ListString([]))
        )
    for text_table in list_map:
        for col in list_values:
            col.extend(
                text_table[col.col_name]
            )
    _final = TableDocuments(list_values)
    _col_keys = _final.get_column(ColumnsTable.KEY)
    for n, v in enumerate(_col_keys):
        _col_keys[n] = f'{n}'
    _final.set_column(_col_keys)
    return _final

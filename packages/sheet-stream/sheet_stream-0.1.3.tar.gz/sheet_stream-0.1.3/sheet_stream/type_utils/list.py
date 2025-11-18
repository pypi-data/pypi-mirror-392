#!/usr/bin/env python3
from __future__ import annotations
from sheet_stream.erros import InvalidTypeObject
from typing import TypeVar, Generic, Type


def contains(text: str, values: list[str], *, case: bool = True, iqual: bool = False) -> bool:
    """
        Verificar se um texto existe em lista de strings.
    """
    if case:
        if iqual:
            for x in values:
                if text == x:
                    return True
        else:
            for x in values:
                if text in x:
                    return True
    else:
        if iqual:
            for x in values:
                if text.upper() == x.upper():
                    return True
        else:
            for x in values:
                if text.upper() in x.upper():
                    return True
    return False


def find_index(text: str, values: list[str], *, case: bool = True, iqual: bool = False) -> int | None:
    """
        Verificar se um texto existe em lista de ‘strings’ se existir, retorna o índice da posição
    do texto na lista.
    """
    _idx: int | None = None
    if case:
        if iqual:
            for num, x in enumerate(values):
                if text == x:
                    _idx = num
                    break
        else:
            for num, x in enumerate(values):
                if text in x:
                    _idx = num
                    break
    else:
        if iqual:
            for num, x in enumerate(values):
                if text.upper() == x.upper():
                    _idx = num
                    break
        else:
            for num, x in enumerate(values):
                if text.upper() in x.upper():
                    _idx = num
                    break
    return _idx


def find_all_index(text: str, values: list[str], *, case: bool = True, iqual: bool = False) -> list[int]:
    """

    """
    items: list[int] = ListItems([])
    if iqual:
        for num, i in enumerate(values):
            if case:
                if i == text:
                    items.append(num)
            else:
                if text.lower() == i.lower():
                    items.append(num)
    else:
        for num, i in enumerate(values):
            if case:
                if text in i:
                    items.append(num)
            else:
                if text.lower() in i.lower():
                    items.append(num)
    return items


T = TypeVar('T')


class ListItems(list[T], Generic[T]):

    def __init__(self, items: list = None):
        if items is None:
            super().__init__([])
        else:
            super().__init__(items)
        self.__list_type: Type[T] = object

    @property
    def first(self) -> T:
        return self[0]

    @property
    def last(self) -> T:
        return self[-1]

    @property
    def length(self) -> int:
        return len(self)

    @property
    def is_empty(self) -> bool:
        return self.length == 0

    def set_list_type(self, cls_type=object):
        self.__list_type = cls_type

    def get_list_type(self) -> object:
        return self.__list_type

    def get(self, idx: int):
        return self[idx]

    def set(self, idx: int, value) -> None:
        self[idx] = value

    def exists(self, item) -> bool:
        """
        Verifica se um objeto existe na lista
        """
        if not isinstance(item, self.__list_type):
            raise InvalidTypeObject(
                f'{__class__.__name__} tipo inválido {type(item)}\nUse: {self.__list_type}'
            )

        for x in self:
            if x.__hash__() == item.__hash__():
                return True
        return False

    def append(self, __object: T):
        if not isinstance(__object, self.__list_type):
            raise ValueError(f'{__class__.__name__} tipo inválido {type(__object)}, use: {self.__list_type}')
        super().append(__object)


class ListString(ListItems):

    def __init__(self, items: ListItems[str] | list[str] = None):
        if isinstance(items, ListItems):
            super().__init__(items)
        else:
            super().__init__(ListItems(items))
        self.set_list_type(str)

    @property
    def first(self) -> str:
        return super().first

    @property
    def last(self) -> str:
        return super().last

    def contains(self, item: str, *, case: bool = True, iqual: bool = False) -> bool:
        return contains(item, self, case=case, iqual=iqual)

    def find_index(self, item: str, *, case: bool = True, iqual: bool = False) -> int | None:
        return find_index(item, self, case=case, iqual=iqual)

    def find_all_index(self, item: str, *, case: bool = True, iqual: bool = False) -> list[int]:
        return find_all_index(item, self, case=case, iqual=iqual)

    def get(self, idx: int) -> str:
        return self[idx]

    def set(self, idx: int, value: str) -> None:
        self[idx] = value

    def append(self, text: str):
        super().append(text)

    def add_item(self, i: str):
        self.append(i)

    def add_items(self, items: list[str]):
        for item in items:
            self.add_item(item)


class ArrayString(ListString):
    """
        Classe para filtrar e manipular lista de strings.
    """

    def __init__(self, items: ListItems[str] | list[str] = None):
        super().__init__(items)

    def get_next_string(self, text: str, *, iqual: bool = False, case: bool = False) -> str | None:
        """
        Ao encontrar o texto 'text' na lista retorna a próxima string se existir, se não retorna None.
        """
        next_idx: int | None = self.get_next_index(text, iqual=iqual, case=case)
        return None if next_idx is None else self[next_idx]

    def get_next_all(self, text: str, iqual: bool = False, case: bool = False) -> ListString:
        next_idx: int | None = self.get_next_index(text, iqual=iqual, case=case)
        return ListString() if next_idx is None else ListString(ListItems(self[next_idx:]))

    def get_next_index(self, text: str, *, iqual: bool = False, case: bool = False) -> int | None:
        """
            Ao encontrar o texto 'text' na lista retorna o índice da string anterior
        se existir, se não retorna None.
        """
        _idx: int | None = self.find_index(text, iqual=iqual, case=case)
        if _idx is None:
            return None
        if _idx < 0:
            return None
        if _idx >= self.length - 1:
            return None
        return _idx + 1

    def get_back_index(self, text: str, *, iqual: bool = False, case: bool = False) -> int | None:
        """
            Ao encontrar o texto 'text' na lista retorna o índice da string anterior
        se existir, se não retorna None.
        """
        _final_idx: int | None = self.find_index(text, iqual=iqual, case=case)
        if _final_idx is None:
            return None
        if _final_idx <= 0:
            return None
        return _final_idx - 1

    def get_back_string(self, text: str, iqual: bool = False, case: bool = False) -> str | None:
        """
        Ao encontrar o texto 'text' na lista retorna a string anterior se existir, se não retorna None.
        """
        _idx = self.get_back_index(text, iqual=iqual, case=case)
        return None if _idx is None else self[_idx]

    def get_back_all(self, text: str, iqual: bool = False, case: bool = False) -> ListString:
        _idx = self.get_back_index(text, iqual=iqual, case=case)
        return ListString([]) if _idx is None else ListString(self[:_idx])

    def get(self, idx: int) -> str:
        return self[idx]

    def find_text(self, text: str, *, iqual: bool = False, case: bool = False) -> str | None:
        if (text is None) or (text == ""):
            raise ValueError(f'{__class__.__name__}: text is None')
        idx_item = self.find_index(text, iqual=iqual, case=case)
        return None if idx_item is None else self[idx_item]

    def find_all(self, text: str, *, iqual: bool = False, case: bool = True) -> ListString:
        list_idx: list[int] = find_all_index(text, self, case=case, iqual=iqual)
        if len(list_idx) == 0:
            return ListString([])

        new_values = ListString([])
        for idx in list_idx:
            new_values.append(self[idx])
        return new_values

    def count(self, text: str, *, iqual: bool = False, case: bool = True) -> int:
        count: int = 0
        if iqual:
            for i in self:
                if case:
                    if i == text:
                        count += 1
                else:
                    if text.lower() == i.lower():
                        count += 1
        else:
            for i in self:
                if case:
                    if text in i:
                        count += 1
                else:
                    if text.lower() in i.lower():
                        count += 1
        return count


class HeadCell(str):

    def __init__(self, text: str):
        super().__init__()
        self.text: str = text


class HeadValues(ListString):

    def __init__(self, head_items: list[HeadCell] = None):
        super().__init__(head_items)
        self.set_list_type(HeadCell)

    def contains(self, item: HeadCell | str, *, case: bool = True, iqual: bool = False) -> bool:
        return contains(item, self, case=case, iqual=iqual)

    def get(self, idx: int) -> HeadCell:
        return self[idx]

    def add_item(self, i: HeadCell | str):
        if isinstance(i, str):
            i = HeadCell(i)
        self.append(i)


class ListColumnBody(ArrayString):
    """
        Lista de strings nomeada para representar os dados da coluna de uma tabela.
    """

    def __init__(self, col_name: HeadCell | str, col_body: list[str]):
        super().__init__(col_body)
        if isinstance(col_name, str):
            col_name = HeadCell(col_name)
        self.col_name: HeadCell = col_name

    def __repr__(self):
        return f'{__class__.__name__}\nName: {self.col_name}\nValues:{super().__repr__()}'

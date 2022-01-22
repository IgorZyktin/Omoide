# -*- coding: utf-8 -*-
"""Paginator that works with arbitrary items as pages.
"""
from typing import TypeVar, Sequence, Iterator, Generic

from pydantic import BaseModel

T = TypeVar('T')


class PageVal(Generic[T], BaseModel):
    """Single page representation."""
    number: int
    value: T | None
    is_dummy: bool
    is_current: bool


class Album(Generic[T]):
    """Paginator that works with arbitrary items as pages."""

    def __init__(
            self,
            sequence: Sequence[T],
            position: T | None,
            items_on_page: int,
    ) -> None:
        """Initialize instance."""
        try:
            self.index = sequence.index(position)
            self.number = self.index + 1
        except ValueError:
            self.index = -1
            self.number = 0
        self.position = position
        self.sequence = sequence
        self.total_items = len(sequence)
        self.items_on_page = items_on_page
        self.window = items_on_page // 2

    def __repr__(self) -> str:
        """Return string representation."""
        if len(self.sequence) > 5:
            seq = repr(self.sequence[:5]) + '...'
        else:
            seq = repr(self.sequence)

        _class = type(self).__name__
        return (
            f'{_class}('
            f'sequence={seq}, '
            f'position={self.position!r}, '
            f'items_on_page={self.items_on_page}'
            ')'
        )

    def __iter__(self) -> Iterator[PageVal]:
        """Iterate over current page."""
        if self.is_fitting:
            # [1][2][3][4][5]
            yield from self._iterate_short()
        else:
            # [1][...][55][56][57][...][70]
            yield from self._iterate_long()

    def __len__(self) -> int:
        """Return total amount of items in the sequence."""
        return self.total_items

    @property
    def is_fitting(self) -> bool:
        """Return True if all pages can be displayed at once."""
        return self.total_items <= self.items_on_page

    @classmethod
    def empty(cls) -> 'Album':
        """Create empty paginator."""
        return cls(
            sequence=[],
            position=None,
            items_on_page=1,
        )

    @property
    def has_previous(self) -> bool:
        """Return True if we can go back."""
        return self.index > 0

    @property
    def has_next(self) -> bool:
        """Return True if we can go further."""
        return 0 <= self.index < self.total_items - 1

    @property
    def previous_item(self) -> T | None:
        """Return previous value in sequence."""
        if self.has_previous:
            return self.sequence[self.index - 1]
        return None

    @property
    def next_item(self) -> T | None:
        """Return next value in sequence."""
        if self.has_next:
            return self.sequence[self.index + 1]
        return None

    @property
    def first_item(self) -> T | None:
        """Return first item."""
        if self.sequence:
            return self.sequence[0]
        return None

    @property
    def last_item(self) -> T | None:
        """Return last item."""
        if self.sequence:
            return self.sequence[-1]
        return None

    def _iterate_short(self) -> Iterator[PageVal]:
        """Iterate over all pages, no exclusions."""
        for number, value in enumerate(self.sequence, start=1):
            yield PageVal(
                number=number,
                value=value,
                is_dummy=False,
                is_current=number == self.number,
            )

    def _iterate_long(self) -> Iterator[PageVal]:
        """Iterate over all pages, but show only some of them."""
        left_threshold = self.window
        right_threshold = self.total_items - self.window - 1

        if self.index < left_threshold:
            yield from self._left_leaning_design()
        elif self.index > right_threshold:
            yield from self._right_leaning_design()
        else:
            yield from self._centered_design()

    def _left_leaning_design(self) -> Iterator[PageVal]:
        """Render like [1][2][3][4][...][9]."""
        section = self.sequence[:self.items_on_page - 2]
        for number, value in enumerate(section, start=1):
            yield PageVal(
                value=value,
                number=number,
                is_dummy=False,
                is_current=number == self.number,
            )

        yield PageVal(
            value=None,
            number=-1,
            is_dummy=True,
            is_current=False,
        )

        yield PageVal(
            value=self.last_item,
            number=self.total_items,
            is_dummy=False,
            is_current=self.total_items == self.number,
        )

    def _centered_design(self) -> Iterator[PageVal]:
        """Render like [1][...][10][11][12][...][45]."""
        yield PageVal(
            value=self.first_item,
            number=1,
            is_dummy=False,
            is_current=self.number == 1,
        )

        yield PageVal(
            value=None,
            number=-1,
            is_dummy=True,
            is_current=False,
        )

        left = self.index - self.window // 2
        right = self.index + self.window // 2 + 1

        for i in range(left, right + 1):
            yield PageVal(
                value=self.sequence[i],
                number=i + self.window // 2,
                is_dummy=False,
                is_current=i + 1 == self.number,
            )

        yield PageVal(
            value=None,
            number=-1,
            is_dummy=True,
            is_current=False,
        )

        yield PageVal(
            value=self.last_item,
            number=self.total_items,
            is_dummy=False,
            is_current=self.total_items == self.number,
        )

    def _right_leaning_design(self) -> Iterator[PageVal]:
        """Render like [1][...][7][8][9]."""
        yield PageVal(
            value=self.first_item,
            number=1,
            is_dummy=False,
            is_current=self.number == 1,
        )

        yield PageVal(
            value=None,
            number=-1,
            is_dummy=True,
            is_current=False,
        )

        taken = 2
        start = self.total_items - self.items_on_page + taken
        section = self.sequence[start:]
        for number, value in enumerate(section, start=start + taken - 1):
            yield PageVal(
                value=value,
                number=number,
                is_dummy=False,
                is_current=number == self.number,
            )

#!/usr/bin/env python
# coding: utf-8
"""
    package.module
    ~~~~~~~~~~~~~

    A description which can be long and explain the complete
    functionality of this module even with indented code examples.
    Class/Function however should not be documented here.

    :copyright: 2017, Jonathan Racicot, see AUTHORS for more details
    :license: MIT, see LICENSE for more details
"""
import textblob
from resyst.codeobject import LabelledObject

class TextObject(LabelledObject):
    def __init__(self, _textdata):
        super().__init__()
        self._text = _textdata

    def __str__(self):
        fmt = "<TextObject Size={s:d} character(s)>"
        return fmt.format(s=len(self._text))

    def __len__(self):
        """
        Returns the length of the text object.
        """
        return len(self._text)

    def __eq__(self, _other):
        """
        Verifies if this object is equal to the object provided.

        To be equivalent, the object provided must be:
        1) A TextObject; and
        2) Contain the same text data.

        @param _other The object to compare with
        @return True if the other object is a BinaryObject containing the same
        data.
        """
        if isinstance(_other, self.__class__):
            return self._text == _other._text
        return False

    def __ne__(self, _other):
        """
        Verifies if this object is unequal to the object provided.

        To be equivalent, the object provided must be:
        1) A TextObject; and
        2) Contain the same text data.

        @param _other The object to compare with
        @return True if the other object is a not TextObject or does not contain
        the same data.
        """
        return not self.__eq__(_other)

    @property
    def get_text(self):
        """
        Returns the data currently held by this object.

        @return Data contained in this object.
        """
        return self._text

    def noun_phrases(self):
        tb = textblob.TextBlob(self._text)
        return tb.noun_phrases

    def split_in_chunks(self, _chunk_size):
        """
        Divides the current TextObject into smaller TextObject objects containing
        the textual data of the current object.

        :param _chunk_size: The chunk size of TextObject created. Must be greater than 0.
        :return: A list of TextObject containing text chunk of the current object.
        """
        assert _chunk_size > 0
        chunks = [TextObject(self._text[i:i + _chunk_size]) for i in range(0, len(self._text), _chunk_size)]
        return chunks

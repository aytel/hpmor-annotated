# -*- coding: utf-8 -*-
"""Где лежат исходники и куда класть результат.
HPMOR_SRC — каталог с тремя PDF печатного издания и исходными hpmor_ru.epub / .fb2.
HPMOR_OUT — каталог для собранных книг (по умолчанию текущий)."""
import os

SRC = os.environ.get("HPMOR_SRC", os.path.expanduser("~/Documents/hpmor"))
OUT = os.environ.get("HPMOR_OUT", ".")
PDFS = ["Книга 1.pdf", "Книга 2.pdf", "Книга 3.pdf"]
EPUB_IN = os.path.join(SRC, "hpmor_ru.epub")
FB2_IN = os.path.join(SRC, "hpmor_ru.fb2")
EPUB_OUT = os.path.join(OUT, "hpmor_ru.annotated.epub")
FB2_OUT = os.path.join(OUT, "hpmor_ru.annotated.fb2")

# -*- coding: utf-8 -*-
"""quickstart.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1OgI8VgZGQAeKa60EXX0sdSbKP-aO8cjf

### Install
"""





import importlib
import gmft
import gmft.table_detection
import gmft.table_visualization
import gmft.table_function
import gmft.table_function_algorithm
import gmft.table_captioning
import gmft.pdf_bindings.bindings_pdfium
import gmft.pdf_bindings
import gmft.common

importlib.reload(gmft)
importlib.reload(gmft.common)
importlib.reload(gmft.table_captioning)
importlib.reload(gmft.table_detection)
importlib.reload(gmft.table_visualization)
importlib.reload(gmft.table_function)
importlib.reload(gmft.table_function_algorithm)
importlib.reload(gmft.pdf_bindings.bindings_pdfium)
importlib.reload(gmft.pdf_bindings)

"""### Paper 1: TATR

We will use the original paper that introduced the Table Transformer (TATR): "PubTables-1M: Towards comprehensive table extraction from unstructured documents" by Smock, Pesala, and Abraham.
"""

# get the PubTables-1M paper, source of original Table Transformer (TATR)
#!mkdir ./samples
#!wget -O ./samples/tatr.pdf -q https://arxiv.org/pdf/2110.00061

from gmft.pdf_bindings import PyPDFium2Document
from gmft.auto import CroppedTable, AutoTableDetector

detector = AutoTableDetector()

def ingest_pdf(pdf_path) -> list[CroppedTable]:
    doc = PyPDFium2Document(pdf_path)

    tables = []
    for page in doc:
        tables += detector.extract(page)
    return tables, doc

tables, doc = ingest_pdf('./samples/tatr.pdf')
len(tables)

"""There are 6 matches. Let's view them."""

# display several images
# decrease size with plt
for table in tables:
    table.visualize(figsize=None)

"""In gmft, a `CroppedTable` is a region where a table has been detected. However, for speed, the text is not automatically extracted. To do this, you will need a `TableFormatter`. Specifically, the `AutoTableFormatter` is recommended (which currently points to `TATRTableFormatter`).

Let's work through the tables in order.
"""

from gmft.auto import AutoTableFormatter

formatter = AutoTableFormatter()

ft = formatter.extract(tables[0])
ft.visualize()

"""Since table #1 is an **image**, OCR is required (which you must handle externally.) The image can be obtained through ft.image(), which is a PIL image. This image can then be fed into an OCR of your choice, like paddlepaddle, tesseract, even GPT4 vision, etc."""

ft.image(dpi=144)

"""Let's keep going."""

ft = formatter.extract(tables[1])
ft.image()

ft.df()

"""Now that table has text, gmft can extract. You can call `table.text()` and `table.text_positions()` to, for instance, to filter results by keyword before parsing the table."""

tables[1].text()

"""New in `v0.2`, gmft can also detect table captions."""

tables[1].captions()

# 1s
ft = formatter.extract(tables[2])
ft.image(dpi=50)

"""It looks like table #3 is a false positive. The confidence score is also lower."""

tables[2].label, tables[2].confidence_score

"""Undeterred, let's see table #4."""


ft = formatter.extract(tables[3])
ft.df()

"""There is a hierarchical header. New in `v0.2`, gmft can handle this."""

from gmft.auto import AutoFormatConfig


config_hdr = AutoFormatConfig() # config may be passed like so
config_hdr.verbosity = 3
config_hdr.enable_multi_header = True
config_hdr.semantic_spanning_cells = True # [Experimental] Merge headers

import pandas as pd


"""Config overrides can also be passed into the formatter."""

config = AutoFormatConfig() # config may be passed like so
config.verbosity = 3
config.enable_multi_header = False # This option disables pandas multi-headers
config.semantic_spanning_cells = True # But spanning cells can still be semantically analyzed
custom_formatter = AutoTableFormatter(config=config)

ft = custom_formatter.extract(tables[3])
ft.df()

"""Tables #5 is straightforward."""

ft = formatter.extract(tables[4])
ft.df()

"""Table #6 has a hierarchical left header, now supported in `v0.2`. Relevant config settings are `TATRFormatConfig.semantic_spanning_cells=True` and `TATRFormatConfig.semantic_hierarchical_left_fill`"""

ft = formatter.extract(tables[5])
ft.df(config_overrides=config_hdr)

"""Important! With PyPDFium2, remember to close documents once you're done. This is especially important in loops."""

doc.close()

"""### Paper 2: Attention

Let's look at the classic paper [Attention is All You Need](https://arxiv.org/abs/1706.03762) by Viswani et al.
"""

#!wget -O ./samples/attention.pdf -q https://arxiv.org/pdf/1706.03762

tables, doc = ingest_pdf('./samples/attention.pdf')
len(tables)

# decrease size with plt
for table in tables:
    table.visualize(figsize=None)

ft = formatter.extract(tables[1])
ft.df()

ft = formatter.extract(tables[2])

ft = formatter.extract(tables[3])
ft.df().fillna('')

ft = formatter.extract(tables[4])
ft.df()

doc.close()

"""If you ever want to use a table after having closed the document, you can try the following:
`PyPDFium2Utils.reload`
"""

from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Utils


ft, doc = PyPDFium2Utils.reload(ft)

ft.captions()

doc.close()

"""### Paper 3: NMR

Let's push the limit by extracting a difficult table with a lot of rows.
"""

#!wget -O ./samples/nmr.pdf -q http://ccc.chem.pitt.edu/wipf/Web/NMR_Impurities.pdf

tables, doc = ingest_pdf('./samples/nmr.pdf')
len(tables)

print(tables[0].confidence_score)
tables[0].image()

# display several images
for table in tables:
    table.visualize(figsize=None)

# 4s
ft1 = formatter.extract(tables[1])
ft1.visualize(filter=[2,3], show_labels=False, margin='auto', figsize=(16, 10), linewidth=1)

"""TATR's row detection may struggle for large tables. Thus, for large tables gmft uses a procedural algorithm which takes advantage of the greater number of rows. This is called the **large table assumption**, and it can be configured on/off."""

ft1.visualize(filter=[2,3], effective=True, margin='auto', figsize=(16, 10), show_labels=False, linewidth=1)

import pandas as pd

"""Usually, having an excess of rows is better than having too few rows. This is because gmft will prune empty rows, while too few rows means that rows get merged.

The image -> df step is heavily dependent on padding (see [this issue](https://github.com/microsoft/table-transformer/issues/158)). Therefore, it may be worth adjusting the padding if you get an unfavorable result.

New in `v0.2`, setting `margin='auto', padding=None` will include 30 pixels of the pdf on all sides, which is used by PubTables-1M authors. I find that this can make a difference for large tables.
"""

ft1 = formatter.extract(tables[1], margin='auto', padding=None)
ft1.visualize(filter=[2,3], effective=False, margin='auto', figsize=(16, 10), show_labels=False, linewidth=1)

"""By default, **large table assumption** activates under these conditions:

At least one of these:
- More than `large_table_if_n_rows_removed` rows are removed (default: >= 8)
- OR all of the following are true:
    - Measured overlap of rows exceeds `large_table_row_overlap_threshold` (default: 20%)
    - AND the number of rows is greater than `large_table_threshold` (default: >= 10)

Large table assumption can be directly turned on/off with `config.large_table_assumption = True/False`.

The warning can be turned off with `config.verbosity = 0`
"""

from gmft.table_function import TATRFormatConfig


config = TATRFormatConfig()
config.verbosity = 0
# config.force_large_table_assumption = True # forces it to always run
config.force_large_table_assumption = False # forces it to never run
ft = formatter.extract(tables[2])

"""Also, be warned that false positives are be observed more often for rotated tables ( where `table.label == 1`)

Finally, useful outlier/warning information may be stored in `ft.outliers`.
"""

ft.outliers

doc.close()

"""### Addendum: Benchmarks

This is run on Google Colab's **cpu**.
"""

import time
_total_detect_time = 0
_total_detect_num = 0
_total_format_time = 0
_total_format_num = 0

for paper in ['tatr.pdf', 'attention.pdf', 'nmr.pdf']:
  start = time.time()
  tables, doc = ingest_pdf('./samples/' + paper)
  num_pages = len(doc)
  end_detect = time.time()
  for table in tables:
    tf = formatter.extract(table)
  end_format = time.time()
  doc.close()
  print(f"Paper: {paper}\nDetect time: {end_detect - start:.3f}s for {num_pages} pages")
  print(f"Format time: {end_format - end_detect:.3f}s for {len(tables)} tables\n")
  _total_detect_time += end_detect - start
  _total_detect_num += num_pages
  _total_format_time += end_format - end_detect
  _total_format_num += len(tables)
print(f"Macro: {_total_detect_time/_total_detect_num:.3f} s/page and {_total_format_time/_total_format_num:.3f} s/table ")

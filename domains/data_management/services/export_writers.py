"""
Writers de arquivos de exportação (CSV e XLSX).

Abstração base + implementações por formato. O writer recebe cabeçalhos e um
iterador de linhas (streaming — não carrega todo o dataset em memória) e grava
no destino informado, retornando a quantidade de registros.

Decisão técnica — XLSX sem dependência nova: o projeto não possui openpyxl e a
geração deve evitar pacotes desnecessários. O XLSX é um ZIP de XML, portanto o
writer usa apenas a stdlib (`zipfile` + `xml.sax.saxutils`). Células numéricas
são tipadas como número; as demais usam `inlineStr`.
"""

import csv
import os
import re
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from xml.sax.saxutils import escape

from domains.data_management.exceptions import ExportValidationException

_NUMBER_RE = re.compile(r'^-?\d+(\.\d+)?$')

# Pacotes XML de um XLSX mínimo (planilha única, inline strings + números).
_XLSX_CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'''

_XLSX_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'''

_XLSX_WORKBOOK = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Exportacao" sheetId="1" r:id="rId1"/></sheets></workbook>'''

_XLSX_WORKBOOK_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'''

_XLSX_SHEET_HEADER = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'''
_XLSX_SHEET_FOOTER = '</sheetData></worksheet>'


class BaseExportWriter(ABC):
    """Contrato comum dos writers de exportação."""

    @abstractmethod
    def write(self, headers, rows, destination):
        """
        Escreve `headers` + itera `rows` no `destination`.

        Retorna a quantidade de registros gravados (sem contar o cabeçalho).
        """


class CsvExportWriter(BaseExportWriter):
    """CSV com delimitador ';' e encoding UTF-8 com BOM (Excel pt-BR)."""

    def write(self, headers, rows, destination):
        count = 0
        with open(destination, 'w', newline='', encoding='utf-8-sig') as fh:
            writer = csv.writer(fh, delimiter=';')
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)
                count += 1
        return count


def _column_letter(index):
    """Converte índice 0-based de coluna em letras de planilha (A, B, ..., Z, AA)."""
    letter = ''
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letter = chr(65 + remainder) + letter
    return letter


def _cell_xml(value, ref):
    """Serializa uma célula: número tipado ou string inline (escapada)."""
    if _NUMBER_RE.match(value):
        return f'<c r="{ref}"><v>{value}</v></c>'
    return (
        f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">'
        f'{escape(value)}</t></is></c>'
    )


def _row_xml(values, row_num):
    """Serializa uma linha completa da planilha."""
    cells = []
    for idx, value in enumerate(values):
        cells.append(_cell_xml(value, f'{_column_letter(idx)}{row_num}'))
    return f'<row r="{row_num}">{"".join(cells)}</row>'


class XlsxExportWriter(BaseExportWriter):
    """
    XLSX mínimo via stdlib (zipfile + xml).

    A planilha é escrita em um arquivo temporário (streaming em disco, sem
    acumular o dataset em memória) e depois empacotada no .xlsx.
    """

    def write(self, headers, rows, destination):
        destination = Path(destination)
        tmp_path = destination.with_suffix(destination.suffix + '.tmp')
        sheet_tmp = tmp_path.with_name(tmp_path.name + '.sheet.xml')
        count = 0
        try:
            with open(sheet_tmp, 'w', encoding='utf-8') as fh:
                fh.write(_XLSX_SHEET_HEADER)
                fh.write(_row_xml(headers, 1))
                row_num = 2
                for row in rows:
                    fh.write(_row_xml(row, row_num))
                    row_num += 1
                    count += 1
                fh.write(_XLSX_SHEET_FOOTER)

            with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('[Content_Types].xml', _XLSX_CONTENT_TYPES)
                zf.writestr('_rels/.rels', _XLSX_RELS)
                zf.writestr('xl/workbook.xml', _XLSX_WORKBOOK)
                zf.writestr('xl/_rels/workbook.xml.rels', _XLSX_WORKBOOK_RELS)
                zf.write(sheet_tmp, 'xl/worksheets/sheet1.xml')
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise
        finally:
            if sheet_tmp.exists():
                sheet_tmp.unlink()

        os.replace(tmp_path, destination)
        return count


_WRITERS = {
    'csv': CsvExportWriter(),
    'xlsx': XlsxExportWriter(),
}


def get_writer(file_format):
    """Retorna o writer do formato solicitado (csv/xlsx)."""
    writer = _WRITERS.get(file_format)
    if writer is None:
        raise ExportValidationException(
            f'Formato de exportação inválido: {file_format!r}.'
        )
    return writer
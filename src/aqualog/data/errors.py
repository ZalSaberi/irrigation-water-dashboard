from __future__ import annotations


class DataLayerError(Exception):
    """Base exception for persistence/import errors."""


class UnsupportedImportFormatError(DataLayerError):
    pass


class ImportSchemaError(DataLayerError):
    pass


class ImportRowError(DataLayerError):
    pass

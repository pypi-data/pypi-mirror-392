from abc import ABC, abstractmethod
from ..datatypes.enums import Datatype
import beartype
import pandas
import geopandas
import os
import validators

# TODO: add a metaclass for methods that are repetitive


class BaseFileReader(ABC):
    def __init__(self):
        self.file_reader_label = "FileReaderBaseClass"

    def type(self):
        return self.file_reader_label

    @beartype.beartype
    @abstractmethod
    def check_source_type(self, file_source: str):
        assert validators.url(file_source) or os.path.isfile(
            file_source
        ), "Invalid file source, must be a valid URL or file path"

    @abstractmethod
    def get_file(self, file_source: str, layer: str = None):
        pass

    @beartype.beartype
    @abstractmethod
    def save(self, file_path: str, file_extension: str = None):
        pass

    @abstractmethod
    def read(self):
        pass


class CSVFileReader(BaseFileReader):
    def __init__(self):
        self.file_reader_label = "CSVFileReader"
        self.file = None
        self.data = None

    def type(self):
        return self.file_reader_label

    @beartype.beartype
    def check_source_type(self, file_source: str):
        super().check_source_type(file_source)

    def get_file(self, file_source: str, layer: str = None):
        return pandas.read_csv(file_source)

    @beartype.beartype
    def save(self, file_path: str):
        self.data.to_csv(file_path)

    @beartype.beartype
    def read(self, file_source: str):
        self.check_source_type(file_source)
        self.file = self.get_file(file_source)
        self.data = pandas.DataFrame(self.file)


class GeoDataFileReader(BaseFileReader):
    def __init__(self):
        self.file_reader_label = "GeoDataFileReader"
        self.data = None

    def type(self):
        return self.file_reader_label

    @beartype.beartype
    def check_source_type(self, file_source: str):
        super().check_source_type(file_source)

    # TODO: add general check for variable types
    def get_file(self, file_source: str, layer: str = None):
        file_extension = os.path.splitext(file_source)[1]

        if file_extension in [".shp", ".geojson"]:
            return geopandas.read_file(file_source)

        elif file_extension == ".gpkg":
            assert layer is False, "Layer name must be provided for GeoPackage files"

            return geopandas.read_file(file_source, layer=layer)

        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    @beartype.beartype
    def save(self, file_path: str, file_extension: str = None):
        if file_extension == "geojson":
            self.data.to_file(file_path, driver="GeoJSON")

        elif file_extension == "gpkg":
            self.data.to_file(file_path, driver="GPKG")

        elif file_extension == "shp":
            self.data.to_file(file_path)

        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    @beartype.beartype
    def read(self, file_source: str, layer: str = None):
        self.check_source_type(file_source)
        self.file = self.get_file(file_source, layer)
        self.data = geopandas.GeoDataFrame(self.file)


class LoopGisReader:
    def __init__(self, fileData, layer=""):
        self._layer = layer
        self._fileData = fileData
        self._reader = [None] * len(Datatype)
        self.file_reader_label = [None] * len(Datatype)
        self._data = [None] * len(Datatype)

    def get_extension(self, file_source):
        return os.path.splitext(file_source)[1]

    def assign_reader(self, file_source):
        file_extension = self.get_extension(file_source)

        if file_extension == ".csv":
            return CSVFileReader()

        elif file_extension in [".shp", ".geojson", ".gpkg"]:
            return GeoDataFileReader()

        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def read(self, datatype: Datatype):
        self._reader[datatype] = self.assign_reader(self._fileData[datatype])
        self.file_reader_label[datatype] = self._reader[datatype].type()
        self._reader[datatype].read(self._fileData[datatype], self._layer)

        return self._reader[datatype].data

    def __call__(self):
        """
        Read all files in the input data
        """

        if self._fileData[Datatype.GEOLOGY] is not None:
            self._data[Datatype.GEOLOGY] = self.read(Datatype.GEOLOGY)

        if self._fileData[Datatype.STRUCTURE] is not None:
            self._data[Datatype.STRUCTURE] = self.read(Datatype.STRUCTURE)

        if self._fileData[Datatype.FAULT] is not None:
            self._data[Datatype.FAULT] = self.read(Datatype.FAULT)

        if self._fileData[Datatype.FOLD] is not None:
            self._data[Datatype.FOLD] = self.read(Datatype.FOLD)

    def save(self, datatype, file_path, file_extension=None):
        self._reader[datatype].save(file_path, file_extension)

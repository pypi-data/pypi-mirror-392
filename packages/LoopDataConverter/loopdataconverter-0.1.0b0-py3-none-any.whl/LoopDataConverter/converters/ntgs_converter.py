# internal imports
from ..datatypes import Datatype
from .base_converter import BaseConverter

# from ..geometry_correction import FaultConnector
from ..utils import (
    convert_dipdir_terms,
    convert_dip_terms,
    convert_tightness_terms,
    convert_displacement_terms,
)

# external imports
import pandas
import geopandas


class NTGSConverter(BaseConverter):
    # TODO: modify class to take fold, fault, and structure layers as arguments
    def __init__(self, data: pandas.DataFrame):
        self.raw_data = data.copy()
        self.update_empty_rows()
        self._type_label = "NTGSConverter"
        self.crs = self.raw_data[Datatype.GEOLOGY].crs
        self._data = None

    def type(self):
        """
        The function `type` returns the `_type_label` attribute of the object.

        Returns
        -------
            The `type` method is returning the value of the `_type_label` attribute of the object.

        """
        return self._type_label

    def update_empty_rows(self):
        """
        The function `update_empty_rows` updates empty rows in the DataFrame with NaN values.

        Parameters
        ----------
            None

        This method operates on the DataFrames stored in the class and replaces all empty values
        (e.g., empty strings, None, NaN) with NaN across the specified tables.
        """

        # List of tables (DataFrames) to update
        tables_to_update = [Datatype.FOLD, Datatype.FAULT, Datatype.STRUCTURE]

        for table in tables_to_update:
            # Replace empty strings, None, or NaN with np.nan in the entire table
            self.raw_data[table] = self.raw_data[table].map(
                lambda x: "NaN" if pandas.isna(x) or x == "" or x is None else x
            )

    def convert_fold_map(self):
        """
        The function `convert_fold_map` converts dip direction, dip, and tightness terms in the raw data
        to degrees.

        """
        # # rename columns
        # if "AxialPlaneDipDir" in self.raw_data[Datatype.FOLD].columns:
        #     self.raw_data[Datatype.FOLD] = self.raw_data[Datatype.FOLD].rename(columns={'AxialPlaneDipDir': 'AxPlDipDir'})
        # if "AxialPlaneDip" in self.raw_data[Datatype.FOLD].columns:
        #     self.raw_data[Datatype.FOLD] = self.raw_data[Datatype.FOLD].rename(columns={'AxialPlaneDip': 'AxPlaneDip'})
        # if "AxialPlane" in self.raw_data[Datatype.FOLD].columns:
        #     self.raw_data[Datatype.FOLD] = self.raw_data[Datatype.FOLD].rename(columns={'AxialPlane': 'AxPlDipDir'})
        # if "AxialPla_1" in self.raw_data[Datatype.FOLD].columns:
        #     self.raw_data[Datatype.FOLD] = self.raw_data[Datatype.FOLD].rename(columns={'AxialPla_1': 'AxPlaneDip'})
        # if "InterlimbA" in self.raw_data[Datatype.FOLD].columns:
        #     self.raw_data[Datatype.FOLD] = self.raw_data[Datatype.FOLD].rename(columns={'InterlimbA': 'Interlimb'})

        # convert dip direction terms to degrees
        self.raw_data[Datatype.FOLD]["AxPlDipDir"] = self.raw_data[Datatype.FOLD][
            "AxPlDipDir"
        ].apply(lambda x: convert_dipdir_terms(x))

        # convert dip terms to degrees
        self.raw_data[Datatype.FOLD]["AxPlDip"] = self.raw_data[Datatype.FOLD]["AxPlDip"].apply(
            lambda x: convert_dip_terms(x, type="fold")
        )
        # convert tightness terms to degrees
        self.raw_data[Datatype.FOLD]["IntlimbAng"] = self.raw_data[Datatype.FOLD][
            "IntlimbAng"
        ].apply(lambda x: convert_tightness_terms(x))

    def convert_fault_map(self):
        """
        The function `convert_fault_map` converts dip direction, dip, and displacement terms to degrees
        in a DataFrame.

        """

        # convert dip direction terms to degrees

        self.raw_data[Datatype.FAULT]["DipDir"] = self.raw_data[Datatype.FAULT]["DipDir"].apply(
            lambda x: convert_dipdir_terms(x)
        )
        # convert dip terms to degrees
        self.raw_data[Datatype.FAULT]["Dip"] = self.raw_data[Datatype.FAULT]["Dip"].apply(
            lambda x: convert_dip_terms(x, type="fault")
        )
        # convert displacement terms to meters
        self.raw_data[Datatype.FAULT]["Displace"] = self.raw_data[Datatype.FAULT]["Displace"].apply(
            lambda x: convert_displacement_terms(x)
        )
        self.raw_data[Datatype.FAULT]["centroid"] = self.raw_data[Datatype.FAULT].geometry.centroid
        self.raw_data[Datatype.FAULT]["centroid_x"] = self.raw_data[Datatype.FAULT].centroid.x
        self.raw_data[Datatype.FAULT]["centroid_y"] = self.raw_data[Datatype.FAULT].centroid.y
        # self.raw_data[Datatype.FAULT]["Strike"] = self.raw_data[Datatype.FAULT]["DipDir"] + 90
        self.raw_data[Datatype.FAULT]["X"] = self.raw_data[Datatype.FAULT].centroid_x
        self.raw_data[Datatype.FAULT]["Y"] = self.raw_data[Datatype.FAULT].centroid_y
        self.raw_data[Datatype.FAULT]["Z"] = 0.0

    def convert_structure_map(self):
        """
        This function filters out rows with a dip value of -99 and no estimated dip value, then converts
        dip estimates to floats by averaging the range.

        """
        # select any rows that has a dip value of -99 and have any estimated dip value
        condition = (self.raw_data[Datatype.STRUCTURE]["Dip"] == -99) & (
            self.raw_data[Datatype.STRUCTURE]["DipEst"] != "NaN"
        )

        # convert dip estimate to float (average of the range)
        self.raw_data[Datatype.STRUCTURE].loc[condition, "Dip"] = (
            self.raw_data[Datatype.STRUCTURE]
            .loc[condition, "DipEst"]
            .apply(lambda x: convert_dip_terms(x, type="structure"))
        )

        # discard any rows that has a dip value of -99 and does not have any estimated dip value
        condition = (self.raw_data[Datatype.STRUCTURE]["Dip"] == -99) & (
            self.raw_data[Datatype.STRUCTURE]["DipEst"] == "NaN"
        )
        self.raw_data[Datatype.STRUCTURE] = self.raw_data[Datatype.STRUCTURE][~condition]
        self.raw_data[Datatype.STRUCTURE]["Strike"] = (
            self.raw_data[Datatype.STRUCTURE]["DipDir"] + 90
        ) % 360
        self.raw_data[Datatype.STRUCTURE]["X"] = self.raw_data[Datatype.STRUCTURE].geometry.x
        self.raw_data[Datatype.STRUCTURE]["Y"] = self.raw_data[Datatype.STRUCTURE].geometry.y
        self.raw_data[Datatype.STRUCTURE]["Z"] = 0.0

    def fault_map_postprocessing(self):
        """
        This function performs post-processing on the different datatypes.

        """

        # Add strike and dip data from the Fault dataset where STRIKE and DIP rows contain a value and not a NaN value
        valid_faults = self.raw_data[Datatype.FAULT].dropna(
            subset=["MSID", "X", "Y", "Z", "DipDir", "Strike", "Dip", "centroid"]
        )
        valid_faults = valid_faults.rename(columns={"MSID": "featureId"})
        valid_faults["geometry"] = valid_faults["centroid"]
        self.raw_data[Datatype.FAULT_ORIENTATION] = geopandas.GeoDataFrame(
            valid_faults[["featureId", "X", "Y", "Z", "DipDir", "Dip", "geometry"]].copy(),
            crs=self.crs,
        )
        # Remove the string part of "featureId"
        self.raw_data[Datatype.FAULT_ORIENTATION]["featureId"] = self.raw_data[
            Datatype.FAULT_ORIENTATION
        ]["featureId"].apply(lambda x: ''.join(filter(str.isdigit, str(x))))
        self.raw_data[Datatype.FAULT] = self.raw_data[Datatype.FAULT].drop(columns="centroid")

        # fault_data = self.raw_data[Datatype.FAULT].copy()
        # fault_connector = FaultConnector(fault_data)
        # fault_connector.connect_faults()
        # processed_fault_data = fault_connector.processed_data

        # return processed_fault_data

    def convert(self):
        """
        The function `convert` performs various conversions and copies the raw data in a Python class.

        """

        if self.raw_data[Datatype.FOLD] is not None:
            self.convert_fold_map()
        if self.raw_data[Datatype.FAULT] is not None:
            self.convert_fault_map()
        if self.raw_data[Datatype.STRUCTURE] is not None:
            self.convert_structure_map()
            self.fault_map_postprocessing()

        self._data = self.raw_data.copy()

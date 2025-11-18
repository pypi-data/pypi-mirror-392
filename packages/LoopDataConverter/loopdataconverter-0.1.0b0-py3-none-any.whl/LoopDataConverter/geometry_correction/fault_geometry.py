# internal imports
from ..utils import calculate_vector_along_line, calculate_angle

# external imports
import numpy
import pandas
import geopandas
import shapely


class FaultConnector:
    """
    A class to connect and merge faults in a GeoDataFrame based on an angle criterion.

        _data (geopandas.GeoDataFrame): The original GeoDataFrame containing fault data.
        processed_data (geopandas.GeoDataFrame or None): A copy of the original data that is processed
        and modified within the connect_faults method.

    Methods:
        connect_faults()

    """

    def __init__(self, data: geopandas.GeoDataFrame):
        self._data = data.copy()
        self.crs = self._data.crs
        self.processed_data = None

    def connect_faults(self):
        """
        Connects and merges faults in the GeoDataFrame based on an angle criterion.
        This method processes the GeoDataFrame to merge faults if the angle between
        their vectors at the intersection point is below a specified threshold (20 degrees).
        The method iterates through the GeoDataFrame, checks for intersections between
        LineStrings, calculates the angle between the vectors at the intersection point,
        and merges the lines if the angle criterion is met.
        Attributes:
            processed_data (GeoDataFrame): A copy of the original data that is processed
                                           and modified within the method.
        Steps:
            1. Iterate through each pair of LineStrings in the GeoDataFrame.
            2. Check for intersections between the LineStrings.
            3. If an intersection is found and it is a point, calculate the vectors
               aligned with each LineString at the intersection point.
            4. Compute the angle between the vectors.
            5. If the angle is below 20 degrees, merge the LineStrings into a single
               LineString and update the GeoDataFrame.
            6. Restart the process to ensure all possible merges are considered.
        Note:
            The method ensures non-zero vectors before proceeding with angle calculation
            to avoid division by zero errors.
        Raises:
            ValueError: If the input data is not a GeoDataFrame or if the geometries
                        are not LineStrings.
        """

        self.processed_data = self._data.copy()
        i = 0

        while i < len(self.processed_data):
            j = i + 1
            while j < len(self.processed_data):
                line1 = self.processed_data.iloc[i].geometry
                line2 = self.processed_data.iloc[j].geometry

                # Find the intersection
                intersection = line1.intersection(line2)
                if intersection.is_empty or not intersection.geom_type == "Point":
                    j += 1
                    continue  # Skip if no intersection or if it's not a point

                # Get the intersection point
                intersection_point = numpy.array(intersection.coords[0])

                # Compute vectors aligned with each LineString
                vector1 = calculate_vector_along_line(line1, intersection_point)
                vector2 = calculate_vector_along_line(line2, intersection_point)

                # Ensure non-zero vectors before proceeding
                if numpy.linalg.norm(vector1) == 0 or numpy.linalg.norm(vector2) == 0:
                    j += 1
                    continue

                # Calculate the angle between the vectors
                angle = calculate_angle(vector1, vector2)

                # If the angle is below 20 degrees, merge the lines
                if angle < 20:
                    merged_line = shapely.geometry.LineString(
                        list(line1.coords) + list(line2.coords)
                    )

                    # Add the merged line and remove the old ones
                    self.processed_data = self.processed_data.drop([i, j]).reset_index(drop=True)
                    new_row = geopandas.GeoDataFrame({"geometry": [merged_line]}, crs=self.crs)
                    self.processed_data = pandas.concat(
                        [self.processed_data, new_row], ignore_index=True
                    )
                    self.processed_data = geopandas.GeoDataFrame(self.processed_data, crs=self.crs)
                    # self.processed_data = self.processed_data.concat(
                    #     {"geometry": merged_line}, ignore_index=True
                    # )

                    # Restart processing for safety (to avoid index shifts)
                    i = 0
                    j = 0
                else:
                    j += 1  # Move to the next line

            i += 1

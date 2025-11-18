import numpy
import shapely
import logging

logging.basicConfig(level=logging.WARNING)


def unit_vector(vector):
    """
    Returns the unit vector of the given vector.

    Parameters:
    vector (numpy.ndarray): A numpy array representing the vector.

    Returns:
    numpy.ndarray: The unit vector of the input vector.
    """
    return vector / numpy.linalg.norm(vector)


def calculate_angle(v1, v2):
    """
    Returns the angle in degrees between two vectors.

    Parameters:
    v1 (array-like): The first vector.
    v2 (array-like): The second vector.

    Returns:
    float: The angle in degrees between the two vectors.
    """

    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = numpy.degrees(numpy.arccos(numpy.clip(numpy.dot(v1_u, v2_u), -1.0, 1.0)))
    return angle


def calculate_vector_along_line(line, intersection_point):
    """Computes a unit vector along the provided LineString, aligned with its direction.

    Parameters:
        line (shapely.geometry.LineString): The LineString object representing the line.
        intersection_point (tuple or list): Coordinates (x, y) of the intersection point.

    Returns:
        numpy.ndarray: A unit vector (array of floats) in the direction of the line.
                       Returns [0, 0, 0] if no valid segment is found.
    """

    # Project the intersection point onto the line to find its position along the line
    proj_point = line.interpolate(line.project(shapely.geometry.Point(intersection_point)))

    # Get the two closest segments of the line around the intersection point
    coords = list(line.coords)
    for i in range(len(coords) - 1):
        start, end = numpy.array(coords[i], dtype=object), numpy.array(coords[i + 1], dtype=object)
        if (
            shapely.geometry.Point(start).distance(proj_point)
            + shapely.geometry.Point(end).distance(proj_point)
        ) == shapely.geometry.Point(start).distance(shapely.geometry.Point(end)):
            # Found the segment containing the projection point
            segment_vector = end - start
            return unit_vector(segment_vector)
        else:
            logging.warning("FaultConnector: No segment found for the intersection point.")
        # Fallback: Return zero vector if no segment is found (shouldn't happen)
        return numpy.array([0, 0, 0])

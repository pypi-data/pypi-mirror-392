
import enum
from typing import ( 
    List,
    Tuple
)

class ComparisonCondition(enum.Enum):
	LESS_THAN : ComparisonCondition 
	GREATER_THAN : ComparisonCondition 

# Shared Core Classes
class XYZ:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        """
        Initializes the XYZ with the given coordinates.

        :param x: X-coordinate.
        :param y: Y-coordinate.
        :param z: Z-coordinate.
        """
        ...

    def X(self) -> float:
        """
        Gets the X-coordinate.

        :return: X-coordinate.
        """
        ...
        
    def Y(self) -> float:
        """
        Gets the Y-coordinate.

        :return: Y-coordinate.
        """
        ...

    def Z(self) -> float:
        """
        Gets the Z-coordinate.

        :return: Z-coordinate.
        """
        ...

    def __add__(self, other: 'XYZ') -> 'XYZ':
        """
        Adds two XYZ vectors.

        :param other: Another XYZ vector.
        :return: Resulting XYZ vector.
        """
        ...

    def __sub__(self, other: 'XYZ') -> 'XYZ':
        """
        Subtracts two XYZ vectors.

        :param other: Another XYZ vector.
        :return: Resulting XYZ vector.
        """
        ...

    def __mul__(self, scalar: float) -> 'XYZ':
        """
        Multiplies XYZ vector by a scalar.

        :param scalar: Scalar value.
        :return: Resulting XYZ vector.
        """
        ...

    def __eq__(self, other: 'XYZ') -> bool:
        """
        Checks equality of two XYZ vectors.

        :param other: Another XYZ vector.
        :return: True if equal, False otherwise.
        """
        ...

    def __ne__(self, other: 'XYZ') -> bool:
        """
        Checks inequality of two XYZ vectors.

        :param other: Another XYZ vector.
        :return: True if not equal, False otherwise.
        """
        ...

    def magnitude(self) -> float:
        """
        Computes the magnitude of the XYZ vector.

        :return: Magnitude.
        """
        ...

    def is_valid(self) -> bool:
        """
        Checks if the XYZ vector is valid.
        
        :return: True if valid, False otherwise.
        """
        ...

    def normalize(self) -> 'XYZ':
        """
        Normalizes the XYZ vector.
        :return: Normalized XYZ vector.
        """
        ...

    def cross_product(self, other: 'XYZ') -> 'XYZ':
        """
        Computes the cross product of two XYZ vectors.

        :param other: Another XYZ vector.
        :return: Resulting XYZ vector.
        """
        ...

    def dot_product(self, other: 'XYZ') -> float:
        """
        Computes the dot product of two XYZ vectors.
        :param other: Another XYZ vector.
        :return: Dot product.
        """
        ...

    def angle_to(self, other: 'XYZ') -> float:
        """
        Computes the angle (in radians) between this vector and another.
        Returns 0.0 if either vector has zero length.
        
        :param other: Another XYZ vector.
        :return: Angle in radians between the two vectors [0, π].
        """
        ...

    def __repr__(self) -> str:
        """
        String representation of the XYZ vector.

        :return: String representation.
        """
        ...

class Color:
	R : int = ...
	G : int = ...
	B : int = ...

class ColorSelection(enum.Enum):
	DEFAULT : ColorSelection 
	RED : ColorSelection 
	LIME : ColorSelection 
	BLUE : ColorSelection 
	YELLOW : ColorSelection 
	CYAN : ColorSelection 
	MAGENTA  : ColorSelection 
	GRAY : ColorSelection
	MAROON : ColorSelection 
	OLIVE : ColorSelection
	GREEN : ColorSelection 
	PURPLE : ColorSelection 
	TEAL : ColorSelection	
	NAVY : ColorSelection

class Palette(object):
	@staticmethod
	def get_color(selection: ColorSelection) -> Color: ...
	@staticmethod
	def get_specific_color(red: int, green: int, blue: int) -> Color: ...
	@staticmethod
	def are_same(c1: Color, c2: Color) -> bool: ...

class Line:
    """
    Represents an infinite line in 3D space defined by a point and direction.
    The line extends infinitely in both directions along the direction vector.
    """
    
    def __init__(self, point: XYZ, direction: XYZ):
        """
        Constructs a line from a point and direction vector.
        
        :param point: A point on the line.
        :param direction: Direction vector (will be normalized).
        """
        ...
    
    @staticmethod
    def from_two_points(point1: XYZ, point2: XYZ) -> 'Line':
        """
        Constructs a line passing through two points.
        
        :param point1: First point on the line.
        :param point2: Second point on the line.
        :return: A new Line instance.
        """
        ...
    
    def is_valid(self) -> bool:
        """
        Checks if the line is valid (has non-zero direction).
        
        :return: True if valid, False otherwise.
        """
        ...
    
    def get_point(self) -> XYZ:
        """
        Gets the reference point on the line.
        
        :return: Point on the line.
        """
        ...
    
    def get_direction(self) -> XYZ:
        """
        Gets the normalized direction vector of the line.
        
        :return: Direction vector.
        """
        ...
    
    def point_at(self, t: float) -> XYZ:
        """
        Gets a point on the line at parameter t.
        Point = point + t * direction
        
        :param t: Parameter value (can be any real number).
        :return: Point on the line.
        """
        ...
    
    def distance_to_point(self, point: XYZ) -> float:
        """
        Calculates the shortest distance from a point to this line.
        
        :param point: The point to measure distance from.
        :return: Distance from point to line.
        """
        ...
    
    def closest_point(self, point: XYZ) -> XYZ:
        """
        Finds the closest point on the line to a given point.
        
        :param point: The point to find closest point to.
        :return: Closest point on the line.
        """
        ...
    
    def is_parallel_to(self, other: 'Line', tolerance: float = 1e-6) -> bool:
        """
        Checks if two lines are parallel within tolerance.
        
        :param other: Another line.
        :param tolerance: Tolerance for parallelism check.
        :return: True if parallel, False otherwise.
        """
        ...
    
    def contains(self, point: XYZ, tolerance: float = 1e-6) -> bool:
        """
        Checks if a point lies on the line within tolerance.
        
        :param point: The point to check.
        :param tolerance: Distance tolerance.
        :return: True if point is on line, False otherwise.
        """
        ...
    
    def distance_to_line(self, other: 'Line') -> float:
        """
        Calculates the shortest distance between two lines.
        Returns 0 if lines intersect or are parallel.
        
        :param other: Another line.
        :return: Distance between lines.
        """
        ...

class Ray:
    """
    Represents a ray (half-line) in 3D space defined by an origin and direction.
    The ray starts at the origin and extends infinitely in the direction vector.
    """
    
    def __init__(self, origin: XYZ, direction: XYZ):
        """
        Constructs a ray from an origin point and direction vector.
        
        :param origin: Starting point of the ray.
        :param direction: Direction vector (will be normalized).
        """
        ...
    
    @staticmethod
    def from_two_points(origin: XYZ, through: XYZ) -> 'Ray':
        """
        Constructs a ray passing through two points, starting at the first point.
        
        :param origin: Starting point of the ray.
        :param through: Point the ray passes through.
        :return: A new Ray instance.
        """
        ...
    
    def is_valid(self) -> bool:
        """
        Checks if the ray is valid (has non-zero direction).
        
        :return: True if valid, False otherwise.
        """
        ...
    
    def get_origin(self) -> XYZ:
        """
        Gets the origin point of the ray.
        
        :return: Origin point.
        """
        ...
    
    def get_direction(self) -> XYZ:
        """
        Gets the normalized direction vector of the ray.
        
        :return: Direction vector.
        """
        ...
    
    def point_at(self, t: float) -> XYZ:
        """
        Gets a point on the ray at parameter t (t >= 0).
        Point = origin + t * direction
        Returns invalid XYZ if t < 0.
        
        :param t: Parameter value (must be non-negative).
        :return: Point on the ray, or invalid XYZ if t < 0.
        """
        ...
    
    def distance_to_point(self, point: XYZ) -> float:
        """
        Calculates the shortest distance from a point to this ray.
        
        :param point: The point to measure distance from.
        :return: Distance from point to ray.
        """
        ...
    
    def closest_point(self, point: XYZ) -> XYZ:
        """
        Finds the closest point on the ray to a given point.
        If the closest point would be behind the origin, returns the origin.
        
        :param point: The point to find closest point to.
        :return: Closest point on the ray.
        """
        ...
    
    def is_parallel_to(self, other: 'Ray', tolerance: float = 1e-6) -> bool:
        """
        Checks if two rays are parallel within tolerance.
        
        :param other: Another ray.
        :param tolerance: Tolerance for parallelism check.
        :return: True if parallel, False otherwise.
        """
        ...
    
    def contains(self, point: XYZ, tolerance: float = 1e-6) -> bool:
        """
        Checks if a point lies on the ray within tolerance.
        
        :param point: The point to check.
        :param tolerance: Distance tolerance.
        :return: True if point is on ray, False otherwise.
        """
        ...
    
    def get_parameter_of_closest_point(self, point: XYZ) -> float:
        """
        Gets the parameter t for the closest point on the ray to a given point.
        Returns 0 if the closest point is the origin.
        
        :param point: The point to find parameter for.
        :return: Parameter t (>= 0).
        """
        ...

class Segment:
    """
    Represents a line segment in 3D space defined by two endpoints.
    The segment is bounded between the start and end points.
    """
    
    def __init__(self, start: XYZ, end: XYZ):
        """
        Constructs a segment from two endpoints.
        
        :param start: Starting point of the segment.
        :param end: Ending point of the segment.
        """
        ...
    
    def is_valid(self) -> bool:
        """
        Checks if the segment is valid (has non-zero length).
        
        :return: True if valid, False otherwise.
        """
        ...
    
    def get_start(self) -> XYZ:
        """
        Gets the starting point of the segment.
        
        :return: Start point.
        """
        ...
    
    def get_end(self) -> XYZ:
        """
        Gets the ending point of the segment.
        
        :return: End point.
        """
        ...
    
    def get_direction(self) -> XYZ:
        """
        Gets the normalized direction vector of the segment.
        
        :return: Direction vector from start to end.
        """
        ...
    
    def get_length(self) -> float:
        """
        Gets the length of the segment.
        
        :return: Segment length.
        """
        ...
    
    def get_midpoint(self) -> XYZ:
        """
        Gets the midpoint of the segment.
        
        :return: Midpoint.
        """
        ...
    
    def point_at(self, t: float) -> XYZ:
        """
        Gets a point on the segment at parameter t (0 <= t <= 1).
        t=0 returns start, t=1 returns end.
        Returns invalid XYZ if t is outside [0,1].
        
        :param t: Parameter value (must be in [0,1]).
        :return: Point on the segment, or invalid XYZ if t outside range.
        """
        ...
    
    def distance_to_point(self, point: XYZ) -> float:
        """
        Calculates the shortest distance from a point to this segment.
        
        :param point: The point to measure distance from.
        :return: Distance from point to segment.
        """
        ...
    
    def closest_point(self, point: XYZ) -> XYZ:
        """
        Finds the closest point on the segment to a given point.
        The result is clamped to the segment endpoints.
        
        :param point: The point to find closest point to.
        :return: Closest point on the segment.
        """
        ...
    
    def is_parallel_to(self, other: 'Segment', tolerance: float = 1e-6) -> bool:
        """
        Checks if two segments are parallel within tolerance.
        
        :param other: Another segment.
        :param tolerance: Tolerance for parallelism check.
        :return: True if parallel, False otherwise.
        """
        ...
    
    def contains(self, point: XYZ, tolerance: float = 1e-6) -> bool:
        """
        Checks if a point lies on the segment within tolerance.
        
        :param point: The point to check.
        :param tolerance: Distance tolerance.
        :return: True if point is on segment, False otherwise.
        """
        ...
    
    def get_parameter_of_closest_point(self, point: XYZ) -> float:
        """
        Gets the parameter t [0,1] for the closest point on the segment.
        
        :param point: The point to find parameter for.
        :return: Parameter t in [0,1].
        """
        ...
    
    def distance_to_segment(self, other: 'Segment') -> float:
        """
        Calculates the shortest distance between two segments.
        
        :param other: Another segment.
        :return: Distance between segments.
        """
        ...
    
    def reversed(self) -> 'Segment':
        """
        Returns a new segment with start and end swapped.
        
        :return: Reversed segment.
        """
        ...

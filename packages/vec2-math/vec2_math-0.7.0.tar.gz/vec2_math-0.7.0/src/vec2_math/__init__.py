"""Simple operations on vectors. All return 2tuples.

:author: Shay Hill
:created: 2023-08-19
"""

from __future__ import annotations

import enum
import math
from collections.abc import Iterable

_Vec2 = tuple[float, float] | Iterable[float]
_TwoVec2 = tuple[tuple[float, float], tuple[float, float]] | Iterable[Iterable[float]]
_LineAbc = tuple[float, float, float] | Iterable[float]


# ==============================================================================
#
# Angle and base LA
#
# ==============================================================================


def det(vec_a: _Vec2, vec_b: _Vec2) -> float:
    """Return determinant of a 2x2 matrix.

    :param vec_a: 2d vector
    :param vec_b: 2d vector
    :return: determinant of the 2x2 matrix where
        vec_a is the first row and vec_b is the second
    """
    ax, ay = vec_a
    bx, by = vec_b
    return ax * by - ay * bx


def dot(vec_a: _Vec2, vec_b: _Vec2) -> float:
    """Return dot product of two 2d vectors.

    :param vec_a: 2d vector
    :param vec_b: 2d vector
    :return: dot product of the vectors
    """
    return sum(x * y for x, y in zip(vec_a, vec_b, strict=True))


def get_signed_angle(vec_a: _Vec2, vec_b: _Vec2) -> float:
    """Calculate the signed angle at a corner defined by two vectors.

    :param vec_a: 2d vector
    :param vec_b: 2d vector
    :return: signed angle between the vectors

    Counterclockwise angles will be positive
    Clockwise angles will be negative
    """
    return math.atan2(det(vec_a, vec_b), dot(vec_a, vec_b))


# ==============================================================================
#
# Vector magnitude
#
# ==============================================================================


def get_norm(vec: _Vec2) -> float:
    """Return Euclidean norm of a 2d vector.

    :param vec: 2d vector
    :return: Euclidean norm of the vector
    """
    return math.sqrt(sum(x**2 for x in vec))


def set_norm(vec: _Vec2, norm: float = 1) -> tuple[float, float]:
    """Scale a 2d vector to a given magnitude.

    :param vec: 2d vector
    :param norm: desired magnitude of the output vector, default is 1
    :return: normalized (then optionally scaled) 2d vector
    :raise ValueError: if trying to scale a zero-length vector to a nonzero length
    """
    input_norm = get_norm(vec)
    if input_norm == 0 and norm != 0:
        except_msg = "cannot scale a zero-length vector to a nonzero length"
        raise ValueError(except_msg)
    if norm == 0:
        return 0, 0
    scale = norm / input_norm
    return vscale(vec, scale)


# ==============================================================================
#
# Vector arithmetic
#
# ==============================================================================


def vscale(vec: _Vec2, scale: float) -> tuple[float, float]:
    """Multiply a 2d vector by a scalar.

    :param vec: 2d vector
    :param scale: scalar for vec
    :return: vec * scale
    """
    x, y = vec
    return x * scale, y * scale


def vadd(vec_a: _Vec2, vec_b: _Vec2) -> tuple[float, float]:
    """Add two 2d vectors.

    :param vec_a: 2d vector
    :param vec_b: 2d vector
    :return: sum of the vectors
    """
    ax, ay = vec_a
    bx, by = vec_b
    return ax + bx, ay + by


def vsub(vec_a: _Vec2, vec_b: _Vec2) -> tuple[float, float]:
    """Subtract two 2d vectors.

    :param vec_a: 2d vector
    :param vec_b: 2d vector
    :return: difference of the vectors
    """
    return vadd(vec_a, vscale(vec_b, -1))


def vmul(vec_a: _Vec2, vec_b: _Vec2) -> tuple[float, float]:
    """Multiply two 2d vectors.

    :param vec_a: 2d vector
    :param vec_b: 2d vector
    :return: product of the vectors
    """
    ax, ay = vec_a
    bx, by = vec_b
    return ax * bx, ay * by


def vdiv(vec_a: _Vec2, vec_b: _Vec2) -> tuple[float, float]:
    """Divide two 2d vectors.

    :param vec_a: 2d vector
    :param vec_b: 2d vector
    :return: quotient of the vectors
    """
    ax, ay = vec_a
    bx, by = vec_b
    return ax / bx, ay / by


# ==============================================================================
#
# Vector intersection
#
# ==============================================================================


def _seg_to_ray(seg: _TwoVec2) -> tuple[tuple[float, float], tuple[float, float]]:
    """Convert a line segment to a ray.

    :param seg: a line segment defined as two points
    :return: a ray defined as a point and a vector
    :raise ValueError: if the points defining the segment are coincident
    """
    pnt_a, pnt_b = seg
    vec = vsub(pnt_b, pnt_a)
    if vec == (0, 0):
        except_msg = "points defining segment are coincident"
        raise ValueError(except_msg)
    xa, ya = pnt_a
    return (xa, ya), vec


def get_ray_xsect_times(ray_a: _TwoVec2, ray_b: _TwoVec2) -> tuple[float, float] | None:
    """Return the time along ray_a that ray_b intersects.

    :param ray_a: a point and a vector from that point
    :param ray_b: a point and a vector from that point
    :return: time along ray_a that ray_b intersects (can be negative)
        and time along ray_b that ray_a intersects. None if parallel.
    """
    pnt_a, vec_a = ray_a
    pnt_b, vec_b = ray_b
    det_ab = det(vec_a, vec_b)
    if det_ab == 0:
        return None
    vec_ab = vsub(pnt_b, pnt_a)
    return det(vec_ab, vec_b) / det_ab, det(vec_ab, vec_a) / det_ab


def get_segment_intersection(
    seg_a: _TwoVec2, seg_b: _TwoVec2
) -> tuple[float, float] | None:
    """Return the intersection of two line segments.

    :param seg_a: a line segment defined as two points
    :param seg_b: a line segment defined as two points
    :return: intersection point of the two line segments.
        None if they do not intersect.
    """
    ray_a, ray_b = _seg_to_ray(seg_a), _seg_to_ray(seg_b)
    t = get_ray_xsect_times(ray_a, ray_b)
    if t is None:
        return None
    ta, tb = t
    if any([ta < 0, ta > 1, tb < 0, tb > 1]):
        return None
    return vadd(ray_a[0], vscale(ray_a[1], ta))


# ==============================================================================
#
# Scaled translations
#
# ==============================================================================


def move_along(pnt: _Vec2, vec: _Vec2, distance: float) -> tuple[float, float]:
    """Move a point along a vector.

    :param pnt: 2d vector
    :param vec: 2d vector
    :param distance: distance to move v1 along v2
    :return: new point
    """
    vec12 = set_norm(vec, distance)
    return vadd(pnt, vec12)


def move_toward(pnt: _Vec2, target: _Vec2, distance: float) -> tuple[float, float]:
    """Move a point toward a target.

    :param pnt: 2d vector
    :param target: 2d vector
    :param distance: distance to move pnt toward target
    :return: new point
    """
    vec = vsub(target, pnt)
    return move_along(pnt, vec, distance)


def vinterp(pnt_a: _Vec2, pnt_b: _Vec2, t: float) -> tuple[float, float]:
    """Linearly interpolate between two points.

    :param pnt_a: 2d vector
    :param pnt_b: 2d vector
    :param t: interpolation time (presumably between 0 and 1)
    :return: interpolated point
    """
    return vadd(vscale(pnt_a, 1 - t), vscale(pnt_b, t))


# ==============================================================================
#
# Rotation
#
# ==============================================================================


def vrotate(vec: _Vec2, angle: float) -> tuple[float, float]:
    """Rotate a 2d vector counterclockwise by an angle in radians.

    :param vec: 2d vector
    :param angle: angle in radians
    :return: rotated vector
    """
    x, y = vec
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    return (x * cos_angle - y * sin_angle, x * sin_angle + y * cos_angle)


def qrotate(vec: _Vec2, quadrants: int) -> tuple[float, float]:
    """Rotate a 2d vector 90 degrees counterclockwise.

    :param vec: 2d vector
    :param quadrants: number of 90 degree clockwise rotations
    :return: rotated vector
    """
    x, y = vec
    quadrants = quadrants % 4
    if quadrants == 0:
        return x, y
    return qrotate((-y, x), quadrants - 1)


def rotate_around(pnt: _Vec2, center: _Vec2, angle: float) -> tuple[float, float]:
    """Rotate a 2d vector counterclockwise by an angle in radians around a center point.

    :param pnt: 2d vector
    :param center: 2d vector
    :param angle: angle in radians
    :return: rotated vector
    """
    return vadd(center, vrotate(vsub(pnt, center), angle))


# ==============================================================================
#
# Projection
#
# ==============================================================================


class _SegOrLine(enum.Enum):
    SEGMENT = enum.auto()
    LINE = enum.auto()


def _project_to_segment_or_line(
    seg_or_line: _SegOrLine, seg_or_line_points: _TwoVec2, point: _Vec2
) -> tuple[float, tuple[float, float]]:
    """Find the closest point on a line or segment to a point.

    :param seg_or_line: _SegOrLine.SEGMENT or _SegOrLine.LINE
    :param seg_or_line_points: points defining the line or segment
    :param point: point
    :return: projection time, closest point on line or segment
    :raise ValueError: if seg_or_line is not _SegOrLine.SEGMENT or _SegOrLine.LINE

    The projection time is the time along the line or segment at which the closest
    point lies.
    """
    seg_a, vec_ab = _seg_to_ray(seg_or_line_points)
    vec_ap = vsub(point, seg_a)
    dot_ap_ab = dot(vec_ap, vec_ab)
    dot_ab_ab = dot(vec_ab, vec_ab)
    projection_time = dot_ap_ab / dot_ab_ab
    if seg_or_line == _SegOrLine.LINE:
        return projection_time, vadd(seg_a, vscale(vec_ab, projection_time))
    if seg_or_line == _SegOrLine.SEGMENT:
        projection_time = max(0, min(1, projection_time))
        return projection_time, vadd(seg_a, vscale(vec_ab, projection_time))
    msg = "seg_or_line must be _SegOrLine.SEGMENT or _SegOrLine.LINE"
    raise ValueError(msg)


def project_to_line(line: _LineAbc, point: _Vec2) -> tuple[float, float] | None:
    """Project a point onto a line in standard normal form.

    :param line: a line defined by ax + by + c = 0
    :param point: point
    :return: closest point on the line to the point
    """
    a, b, c = line
    x, y = point
    d = a**2 + b**2
    if d == 0:
        return None  # Line has zero magnitude
    x_proj = (b * (b * x - a * y) - a * c) / d
    y_proj = (a * (-b * x + a * y) - b * c) / d
    return x_proj, y_proj


def project_to_segment(seg: _TwoVec2, point: _Vec2) -> tuple[float, float]:
    """Find the closest point on a line segment to a point.

    :param seg: line segment define by two points
    :param point: point
    :return: closest point on the line segment to the point
    """
    return _project_to_segment_or_line(_SegOrLine.SEGMENT, seg, point)[1]


# ==============================================================================
#
# Linear Equation
#
# ==============================================================================


def get_standard_form(seg: _TwoVec2) -> tuple[float, float, float]:
    """Compute ax + by + c = 0 where x**2 + y**2 = 1.

    :param seg: a line segment
    :return: a, b, c in ax + by + c = 0
    """
    (a0, b0), (a1, b1) = seg
    a = b0 - b1
    b = a1 - a0
    c = a0 * b1 - a1 * b0
    return a, b, c


def get_line_point_distance(line: _LineAbc, point: _Vec2) -> float:
    """Get the distance between a point and a line in 2D space.

    :param line: a line described as two points on that line
    :param point: a point
    :return: signed distance between point and line

    Positive distances are on the same side of the line as the normal vector. For
    (1, 0), positive distance would be toward (0, 1). For (0, 1), positive distance
    would be toward (-1, 0).
    """
    a, b, c = line
    x, y = point
    return (x * a + y * b + c) / pow(a**2 + b**2, 1 / 2)


def get_segment_point_distance(seg: _TwoVec2, point: _Vec2) -> float:
    """Get the signed distance between a point and the closest point on a line segment.

    :param seg: a line segment
    :param point: a point
    :return: signed distance between point and line segment
    """
    line_point_distance = get_line_point_distance(get_standard_form(seg), point)
    seg_time, proj = _project_to_segment_or_line(_SegOrLine.SEGMENT, seg, point)
    if seg_time in {0, 1}:
        return math.copysign(get_norm(vsub(point, proj)), line_point_distance)
    return line_point_distance


def get_line_intersection(
    line_a: _LineAbc, line_b: _LineAbc
) -> tuple[float, float] | None:
    """Return the intersection of two lines.

    :param line_a: a line defined by ax + by + c = 0
    :param line_b: a line defined by ax + by + c = 0
    :return: intersection point of the two lines or None if they are parallel
    """
    a1, b1, c1 = line_a
    a2, b2, c2 = line_b
    det_ = det((a2, b2), (a1, b1))
    if math.isclose(det_, 0):
        return None  # Lines are parallel
    x = (b2 * c1 - b1 * c2) / det_
    y = (a1 * c2 - a2 * c1) / det_
    return x, y


def get_line_intersection_from_two_segments(
    seg_a: _TwoVec2, seg_b: _TwoVec2
) -> tuple[float, float] | None:
    """Return the intersection of two lines, each defined by two points on that line.

    :param seg_a: a line segment defined as two points
    :param seg_b: a line segment defined as two points
    :return: intersection point of the two lines or None if they are parallel
    """
    line_a = get_standard_form(seg_a)
    line_b = get_standard_form(seg_b)
    return get_line_intersection(line_a, line_b)

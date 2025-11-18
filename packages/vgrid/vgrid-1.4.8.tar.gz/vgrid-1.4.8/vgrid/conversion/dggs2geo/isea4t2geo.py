"""
ISEA4T to Geometry Module

This module provides functionality to convert ISEA4T (Icosahedral Snyder Equal Area Aperture 4 Triangle) cell IDs to Shapely Polygons and GeoJSON FeatureCollection.

Key Functions:
    isea4t2geo: Convert ISEA4T cell IDs to Shapely Polygons
    isea4t2geojson: Convert ISEA4T cell IDs to GeoJSON FeatureCollection
    isea4t2geo_cli: Command-line interface for polygon conversion
    isea4t2geojson_cli: Command-line interface for GeoJSON conversion

Note: This module is only supported on Windows systems due to OpenEaggr dependency.
"""

import json
import argparse
import platform

if platform.system() == "Windows":
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    from vgrid.utils.geometry import fix_isea4t_antimeridian_cells

    isea4t_dggs = Eaggr(Model.ISEA4T)

from vgrid.utils.geometry import isea4t_cell_to_polygon, geodesic_dggs_to_feature
from vgrid.utils.antimeridian import fix_polygon


def isea4t2geo(isea4t_ids, split_antimeridian=False):
    """
    Convert ISEA4T cell IDs to Shapely geometry objects.

    Accepts a single isea4t_id (string) or a list of isea4t_ids. For each valid ISEA4T cell ID,
    creates a Shapely Polygon representing the grid cell boundaries. Skips invalid or
    error-prone cells.

    Parameters
    ----------
    isea4t_ids : str or list of str
        ISEA4T cell ID(s) to convert. Can be a single string or a list of strings.
        Example format: "131023133313201333311333"
    split_antimeridian : bool, optional
        When True, apply antimeridian fixing to the resulting polygons.
        Defaults to False when None or omitted.

    Returns
    -------
    shapely.geometry.Polygon or list of shapely.geometry.Polygon
        If a single ISEA4T cell ID is provided, returns a single Shapely Polygon object.
        If a list of IDs is provided, returns a list of Shapely Polygon objects.
        Each polygon represents the boundaries of the corresponding ISEA4T cell.

    Examples
    --------
    >>> isea4t2geo("131023133313201333311333")
    <shapely.geometry.polygon.Polygon object at ...>

    >>> isea4t2geo(["131023133313201333311333", "131023133313201333311334"])
    [<shapely.geometry.polygon.Polygon object at ...>, <shapely.geometry.polygon.Polygon object at ...>]
    """
    if split_antimeridian is None:
        split_antimeridian = False
    if isinstance(isea4t_ids, str):
        isea4t_ids = [isea4t_ids]
    isea4t_polygons = []
    for isea4t_id in isea4t_ids:
        try:
            isea4t_cell = DggsCell(isea4t_id)
            cell_polygon = isea4t_cell_to_polygon(isea4t_cell)
            resolution = len(isea4t_id) - 2
            if split_antimeridian:
                cell_polygon = fix_polygon(cell_polygon)
            else:
                if resolution == 0:  #
                    cell_polygon = fix_polygon(cell_polygon)
                elif (
                    isea4t_id.startswith("00")
                    or isea4t_id.startswith("09")
                    or isea4t_id.startswith("14")
                    or isea4t_id.startswith("04")
                    or isea4t_id.startswith("19")
                ):
                    cell_polygon = fix_isea4t_antimeridian_cells(cell_polygon)
            isea4t_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(isea4t_polygons) == 1:
        return isea4t_polygons[0]
    return isea4t_polygons


def isea4t2geo_cli():
    """
    Command-line interface for isea4t2geo supporting multiple ISEA4T cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert ISEA4T cell ID(s) to Shapely Polygons"
    )
    parser.add_argument(
        "isea4t",
        nargs="+",
        help="Input isea4t code(s), e.g., isea4t2geo 131023133313201333311333 ...",
    )
    parser.add_argument(
        "--fix-antimeridian",
        action="store_true",
        help="Apply antimeridian fixing to the resulting polygons",
    )
    args = parser.parse_args()
    if platform.system() == "Windows":
        polys = isea4t2geo(args.isea4t, split_antimeridian=args.fix_antimeridian)
        return polys
    else:
        print("ISEA4T is only supported on Windows systems")


def isea4t2geojson(isea4t_ids, split_antimeridian=False):
    """
    Convert ISEA4T cell IDs to GeoJSON FeatureCollection.

    Accepts a single isea4t_id (string) or a list of isea4t_ids. For each valid ISEA4T cell ID,
    creates a GeoJSON feature with polygon geometry representing the grid cell boundaries.
    Skips invalid or error-prone cells.

    Parameters
    ----------
    isea4t_ids : str or list of str
        ISEA4T cell ID(s) to convert. Can be a single string or a list of strings.
        Example format: "131023133313201333311333"
    split_antimeridian : bool, optional
        When True, apply antimeridian fixing to the resulting polygons.
        Defaults to False when None or omitted.

    Returns
    -------
    dict
        A GeoJSON FeatureCollection containing polygon features for each valid ISEA4T cell.
        Each feature includes:
        - geometry: Polygon representing the cell boundaries
        - properties: Contains the ISEA4T cell ID, resolution level, and cell metadata

    Examples
    --------
    >>> isea4t2geojson("131023133313201333311333")
    {'type': 'FeatureCollection', 'features': [...]}

    >>> isea4t2geojson(["131023133313201333311333", "131023133313201333311334"])
    {'type': 'FeatureCollection', 'features': [...]}
    """
    if split_antimeridian is None:
        split_antimeridian = False
    if isinstance(isea4t_ids, str):
        isea4t_ids = [isea4t_ids]
    isea4t_features = []
    for isea4t_id in isea4t_ids:
        try:
            cell_polygon = isea4t2geo(isea4t_id, split_antimeridian=split_antimeridian)
            resolution = len(isea4t_id) - 2
            num_edges = 3
            isea4t_feature = geodesic_dggs_to_feature(
                "isea4t", isea4t_id, resolution, cell_polygon, num_edges
            )
            isea4t_features.append(isea4t_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": isea4t_features}


def isea4t2geojson_cli():
    """
    Command-line interface for isea4t2geojson supporting multiple ISEA4T cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert Open-Eaggr ISEA4T cell ID(s) to GeoJSON"
    )
    parser.add_argument(
        "isea4t",
        nargs="+",
        help="Input isea4t code(s), e.g., isea4t2geojson 131023133313201333311333 ...",
    )
    parser.add_argument(
        "--fix-antimeridian",
        action="store_true",
        help="Apply antimeridian fixing to the resulting polygons",
    )
    args = parser.parse_args()
    if platform.system() == "Windows":
        geojson_data = json.dumps(isea4t2geojson(args.isea4t, split_antimeridian=args.fix_antimeridian))
        print(geojson_data)
    else:
        print("ISEA4T is only supported on Windows systems")

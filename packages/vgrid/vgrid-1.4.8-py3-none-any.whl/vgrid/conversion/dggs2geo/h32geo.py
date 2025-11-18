"""
H3 to Geometry Module

This module provides functionality to convert H3 cell IDs to Shapely Polygons and GeoJSON FeatureCollection.

Key Functions:
    h32geo: Convert H3 cell IDs to Shapely Polygons
    h32geojson: Convert H3 cell IDs to GeoJSON FeatureCollection
    h32geo_cli: Command-line interface for polygon conversion
    h32geojson_cli: Command-line interface for GeoJSON conversion
"""

import json
import argparse
import h3
from shapely.geometry import Polygon
from vgrid.utils.geometry import fix_h3_antimeridian_cells
from vgrid.utils.geometry import geodesic_dggs_to_feature
from vgrid.utils.antimeridian import fix_polygon


def h32geo(h3_ids, split_antimeridian=False):
    """
    Convert H3 cell IDs to Shapely geometry objects.

    Accepts a single h3_id (string) or a list of h3_ids. For each valid H3 cell ID,
    creates a Shapely Polygon representing the grid cell boundaries. Skips invalid or
    error-prone cells.

    Parameters
    ----------
    h3_ids : str or list of str
        H3 cell ID(s) to convert. Can be a single string or a list of strings.
        Example format: "8e65b56628e0d07"
    split_antimeridian : bool, optional
        When True, apply antimeridian fixing to the resulting polygons.
        Defaults to False when None or omitted.

    Returns
    -------
    shapely.geometry.Polygon or list of shapely.geometry.Polygon
        If a single H3 cell ID is provided, returns a single Shapely Polygon object.
        If a list of IDs is provided, returns a list of Shapely Polygon objects.
        Each polygon represents the boundaries of the corresponding H3 cell.

    Examples
    --------
    >>> h32geo("8e65b56628e0d07")
    <shapely.geometry.polygon.Polygon object at ...>

    >>> h32geo(["8e65b56628e0d07", "8e65b56628e6adf"])
    [<shapely.geometry.polygon.Polygon object at ...>, <shapely.geometry.polygon.Polygon object at ...>]
    """
    if split_antimeridian is None:
        split_antimeridian = False
    if isinstance(h3_ids, str):
        h3_ids = [h3_ids]
    h3_polygons = []
    for h3_id in h3_ids:
        try:
            cell_boundary = h3.cell_to_boundary(h3_id)
            filtered_boundary = fix_h3_antimeridian_cells(cell_boundary)
            reversed_boundary = [(lon, lat) for lat, lon in filtered_boundary]
            cell_polygon = Polygon(reversed_boundary)
            if split_antimeridian:
                cell_polygon = fix_polygon(cell_polygon)
            h3_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(h3_polygons) == 1:
        return h3_polygons[0]
    return h3_polygons


def h32geo_cli():
    """
    Command-line interface for h32geo supporting multiple H3 cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert H3 cell ID(s) to Shapely Polygons"
    )
    parser.add_argument(
        "h3",
        nargs="+",
        help="Input H3 cell ID(s), e.g., h32geo 8e65b56628e0d07 8e65b56628e6adf",
    )
    parser.add_argument(
        "--fix-antimeridian",
        action="store_true",
        help="Apply antimeridian fixing to the resulting polygons",
    )
    args = parser.parse_args()
    polys = h32geo(args.h3, split_antimeridian=args.split_antimeridian)
    return polys


def h32geojson(h3_ids, split_antimeridian=False):
    """
    Convert H3 cell IDs to GeoJSON FeatureCollection.

    Accepts a single h3_id (string) or a list of h3_ids. For each valid H3 cell ID,
    creates a GeoJSON feature with polygon geometry representing the grid cell boundaries.
    Skips invalid or error-prone cells.

    Parameters
    ----------
    h3_ids : str or list of str
        H3 cell ID(s) to convert. Can be a single string or a list of strings.
        Example format: "8e65b56628e0d07"
    split_antimeridian : bool, optional
        When True, apply antimeridian fixing to the resulting polygons.
        Defaults to False when None or omitted.

    Returns
    -------
    dict
        A GeoJSON FeatureCollection containing polygon features for each valid H3 cell.
        Each feature includes:
        - geometry: Polygon representing the cell boundaries
        - properties: Contains the H3 cell ID, resolution level, and cell metadata

    Examples
    --------
    >>> h32geojson("8e65b56628e0d07")
    {'type': 'FeatureCollection', 'features': [...]}

    >>> h32geojson(["8e65b56628e0d07", "8e65b56628e6adf"])
    {'type': 'FeatureCollection', 'features': [...]}
    """
    if split_antimeridian is None:
        split_antimeridian = False
    if isinstance(h3_ids, str):
        h3_ids = [h3_ids]
    h3_features = []
    for h3_id in h3_ids:
        try:
            cell_polygon = h32geo(h3_id, split_antimeridian=split_antimeridian)
            resolution = h3_id
            num_edges = 6
            if h3.is_pentagon(h3_id):
                num_edges = 5
            h3_feature = geodesic_dggs_to_feature(
                "h3", h3_id, resolution, cell_polygon, num_edges
            )
            h3_features.append(h3_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": h3_features}


def h32geojson_cli():
    """
    Command-line interface for h32geojson supporting multiple H3 cell IDs.
    """
    parser = argparse.ArgumentParser(description="Convert H3 cell ID(s) to GeoJSON")
    parser.add_argument(
        "h3",
        nargs="+",
        help="Input H3 cell ID(s), e.g., h32geojson 8e65b56628e0d07 8e65b56628e6adf",
    )
    parser.add_argument(
        "--fix-antimeridian",
        action="store_true",
        help="Apply antimeridian fixing to the resulting polygons",
    )
    args = parser.parse_args()
    geojson_data = json.dumps(h32geojson(args.h3, split_antimeridian=args.split_antimeridian))
    print(geojson_data)


if __name__ == "__main__":
    h32geojson_cli()

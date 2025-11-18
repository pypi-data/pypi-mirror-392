import re
import json
import os
import requests
from urllib.parse import urlparse
from vgrid.utils.io import validate_dggal_type, validate_dggrid_type
import shapely.geometry
import shapely
from pyproj import Geod
from shapely.geometry import Point, Polygon, mapping
from shapely.wkt import loads
from shapely.validation import make_valid
from vgrid.dggs.rhealpixdggs.utils import my_round
from vgrid.dggs import s2
from vgrid.dggs.eaggr.enums.shape_string_format import ShapeStringFormat
from vgrid.dggs.eaggr.eaggr import Eaggr
from vgrid.dggs.eaggr.enums.model import Model
from vgrid.utils.antimeridian import fix_polygon
from vgrid.utils.constants import DGGAL_TYPES, AUTHALIC_RADIUS, ICOSA_EDGE_M
import platform
import math
from dggal import *

if platform.system() == "Windows":
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.enums.model import Model

    isea4t_dggs = Eaggr(Model.ISEA4T)
    isea3h_dggs = Eaggr(Model.ISEA3H)


from dggal import *

app = Application(appGlobals=globals())
pydggal_setup(app)

# Initialize Geod with WGS84 ellipsoid
geod = Geod(ellps="WGS84")
# geod = Geod(a=6371007.181, f=0)  # sphere


def fix_h3_antimeridian_cells(hex_boundary, threshold=-128):
    if any(lon < threshold for _, lon in hex_boundary):
        # Adjust all longitudes accordingly
        return [(lat, lon - 360 if lon > 0 else lon) for lat, lon in hex_boundary]
    return hex_boundary


def fix_rhealpix_antimeridian_cells(boundary, threshold=-128):
    if any(lon < threshold for lon, _ in boundary):
        return [(lon - 360 if lon > 0 else lon, lat) for lon, lat in boundary]
    return boundary


def rhealpix_cell_to_polygon(cell):
    vertices = [
        tuple(my_round(coord, 14) for coord in vertex)
        for vertex in cell.vertices(plane=False)
    ]
    if vertices[0] != vertices[-1]:
        vertices.append(vertices[0])
    vertices = fix_rhealpix_antimeridian_cells(vertices)
    return Polygon(vertices)


def fix_isea4t_wkt(isea4t_wkt):
    coords_section = isea4t_wkt[isea4t_wkt.index("((") + 2 : isea4t_wkt.index("))")]
    coords = coords_section.split(",")
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    fixed_coords = ", ".join(coords)
    return f"POLYGON (({fixed_coords}))"


def fix_isea4t_antimeridian_cells(isea4t_boundary, threshold=-100):
    lon_lat = [(float(lon), float(lat)) for lon, lat in isea4t_boundary.exterior.coords]
    if any(lon < threshold for lon, _ in lon_lat):
        adjusted_coords = [(lon - 360 if lon > 0 else lon, lat) for lon, lat in lon_lat]
    else:
        adjusted_coords = lon_lat
    return Polygon(adjusted_coords)


def isea4t_cell_to_polygon(isea4t_cell):
    cell_to_shp = isea4t_dggs.convert_dggs_cell_outline_to_shape_string(
        isea4t_cell, ShapeStringFormat.WKT
    )
    cell_to_shp_fixed = fix_isea4t_wkt(cell_to_shp)
    cell_polygon = loads(cell_to_shp_fixed)
    return cell_polygon


def get_ease_resolution(ease_id):
    """Get the resolution level of an EASE cell ID."""
    try:
        match = re.match(r"L(\d+)\.(.+)", ease_id)
        if not match:
            raise ValueError(f"Invalid EASE ID format: {ease_id}")
        return int(match.group(1))
    except Exception as e:
        raise ValueError(f"Invalid EASE ID <{ease_id}> : {e}")


def isea3h_cell_to_polygon(isea3h_cell):
    cell_to_shape = isea3h_dggs.convert_dggs_cell_outline_to_shape_string(
        isea3h_cell, ShapeStringFormat.WKT
    )
    cell_to_shp_fixed = fix_isea4t_wkt(cell_to_shape)
    cell_polygon = loads(cell_to_shp_fixed)
    fixed_polygon = fix_polygon(cell_polygon)
    return fixed_polygon


def s2_cell_to_polygon(s2_id):
    """
    Convert an S2 cell ID to a Shapely Polygon.
    """
    cell = s2.Cell(s2_id)
    vertices = []
    for i in range(4):
        vertex = s2.LatLng.from_point(cell.get_vertex(i))
        vertices.append((vertex.lng().degrees, vertex.lat().degrees))

    vertices.append(vertices[0])  # Close the polygon

    # Create a Shapely Polygon
    polygon = Polygon(vertices)
    #  Fix Antimerididan:
    fixed_polygon = fix_polygon(polygon)
    return fixed_polygon


def fix_eaggr_wkt(eaggr_wkt):
    coords_section = eaggr_wkt[eaggr_wkt.index("((") + 2 : eaggr_wkt.index("))")]
    coords = coords_section.split(",")
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    fixed_coords = ", ".join(coords)
    return f"POLYGON (({fixed_coords}))"


def graticule_dggs_metrics(cell_polygon):
    min_lon, min_lat, max_lon, max_lat = cell_polygon.bounds
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    cell_width = geod.line_length([min_lon, max_lon], [min_lat, min_lat])
    cell_height = geod.line_length([min_lon, min_lon], [min_lat, max_lat])
    cell_area = abs(geod.geometry_area_perimeter(cell_polygon)[0])
    cell_perimeter = abs(geod.geometry_area_perimeter(cell_polygon)[1])
    return center_lat, center_lon, cell_width, cell_height, cell_area, cell_perimeter


def geodesic_dggs_metrics(cell_polygon, num_edges):
    cell_centroid = cell_polygon.centroid
    center_lat = cell_centroid.y
    center_lon = cell_centroid.x
    cell_area = abs(geod.geometry_area_perimeter(cell_polygon)[0])
    cell_perimeter = abs(geod.geometry_area_perimeter(cell_polygon)[1])
    avg_edge_len = cell_perimeter / num_edges
    return center_lat, center_lon, avg_edge_len, cell_area, cell_perimeter


def graticule_dggs_to_feature(dggs_type, cell_id, resolution, cell_polygon):
    center_lat, center_lon, cell_width, cell_height, cell_area, cell_perimeter = (
        graticule_dggs_metrics(cell_polygon)
    )
    feature = {
        "type": "Feature",
        "geometry": mapping(cell_polygon),
        "properties": {
            f"{dggs_type}": str(cell_id),
            "resolution": resolution,
            "center_lat": center_lat,
            "center_lon": center_lon,
            "cell_width": cell_width,
            "cell_height": cell_height,
            "cell_area": cell_area,
            "cell_perimeter": cell_perimeter,
        },
    }
    return feature


def geodesic_dggs_to_feature(dggs_type, cell_id, resolution, cell_polygon, num_edges):
    center_lat, center_lon, avg_edge_len, cell_area, cell_perimeter = (
        geodesic_dggs_metrics(cell_polygon, num_edges)
    )
    feature = {
        "type": "Feature",
        "geometry": mapping(cell_polygon),
        "properties": {
            f"{dggs_type}": str(cell_id),
            "resolution": resolution,
            "center_lat": center_lat,
            "center_lon": center_lon,
            "avg_edge_len": avg_edge_len,
            "cell_area": cell_area,
            "cell_perimeter": cell_perimeter,
        },
    }
    return feature


def graticule_dggs_to_geoseries(dggs_type, cell_id, resolution, cell_polygon):
    center_lat, center_lon, cell_width, cell_height, cell_area, cell_perimeter = (
        graticule_dggs_metrics(cell_polygon)
    )
    return {
        f"{dggs_type}": str(cell_id),
        "resolution": resolution,
        "center_lat": center_lat,
        "center_lon": center_lon,
        "cell_width": cell_width,
        "cell_height": cell_height,
        "cell_area": cell_area,
        "cell_perimeter": cell_perimeter,
        "geometry": cell_polygon,
    }


def geodesic_dggs_to_geoseries(dggs_type, cell_id, resolution, cell_polygon, num_edges):
    center_lat, center_lon, avg_edge_len, cell_area, cell_perimeter = (
        geodesic_dggs_metrics(cell_polygon, num_edges)
    )
    return {
        f"{dggs_type}": str(cell_id),
        "resolution": resolution,
        "center_lat": center_lat,
        "center_lon": center_lon,
        "avg_edge_len": avg_edge_len,
        "cell_area": cell_area,
        "cell_perimeter": cell_perimeter,
        "geometry": cell_polygon,
    }


def shortest_point_distance(points):
    """
    Calculate distances between points in a Shapely geometry.
    If there's only one point, return 0.
    If there are multiple points, calculate Delaunay triangulation and return distances.

    Args:
        points: Shapely Point or MultiPoint geometry

    Returns:
        tuple: shortest_distance
    """
    # Handle single Point
    if isinstance(points, Point):
        return 0  # Single point has no distance to other points

    # Handle MultiPoint with single point
    if len(points.geoms) == 1:
        return 0

    # Generate Delaunay triangulation
    delaunay = shapely.delaunay_triangles(points, only_edges=True)

    # Find the shortest edge
    shortest_distance = float("inf")

    for line in delaunay.geoms:
        # Get the coordinates of the line endpoints
        coords = list(line.coords)
        lon1, lat1 = coords[0]
        lon2, lat2 = coords[1]

        # Calculate the distance in meters using pyproj Geod
        distance = geod.inv(lon1, lat1, lon2, lat2)[
            2
        ]  # [2] gives the distance in meters
        if distance < shortest_distance:
            shortest_distance = distance

    return shortest_distance if shortest_distance != float("inf") else 0


def geodesic_distance(
    lat: float, lon: float, length_meter: float
) -> tuple[float, float]:
    """
    Convert meters to approximate degree offsets at a given location.

    Parameters:
        lat (float): Latitude of the reference point
        lon (float): Longitude of the reference point
        length_meter (float): Distance in meters

    Returns:
        (delta_lat_deg, delta_lon_deg): Tuple of degree offsets in latitude and longitude
    """
    # Move north for latitude delta
    lon_north, lat_north, _ = geod.fwd(lon, lat, 0, length_meter)
    delta_lat = lat_north - lat

    # Move east for longitude delta
    lon_east, lat_east, _ = geod.fwd(lon, lat, 90, length_meter)
    delta_lon = lon_east - lon

    return delta_lat, delta_lon


def geodesic_buffer(polygon, distance):
    """
    Create a geodesic buffer around a polygon using pyproj Geod.

    Args:
        polygon: Shapely Polygon geometry
        distance: Buffer distance in meters

    Returns:
        Shapely Polygon: Buffered polygon
    """
    buffered_coords = []
    for lon, lat in polygon.exterior.coords:
        # Generate points around the current vertex to approximate a circle
        circle_coords = [
            geod.fwd(lon, lat, azimuth, distance)[
                :2
            ]  # Forward calculation: returns (lon, lat, back_azimuth)
            for azimuth in range(0, 360, 10)  # Generate points every 10 degrees
        ]
        buffered_coords.append(circle_coords)

    # Flatten the list of buffered points and form a Polygon
    all_coords = [coord for circle in buffered_coords for coord in circle]
    return Polygon(all_coords).convex_hull


def check_predicate(cell_polygon, input_geometry, predicate=None):
    """
    Determine whether to keep an H3 cell based on its relationship with the input geometry.

    Args:
        cell_polygon: Shapely Polygon representing the H3 cell
        input_geometry: Shapely geometry (Polygon, LineString, etc.)
        predicate (str or int): Spatial predicate to apply:
            String values:
                None or "intersects": intersects (default)
                "within": within
                "centroid_within": centroid_within
                "largest_overlap": intersection >= 50% of cell area
            Integer values (for backward compatibility):
                None or 0: intersects (default)
                1: within
                2: centroid_within
                3: intersection >= 50% of cell area

    Returns:
        bool: True if cell should be kept, False otherwise
    """
    # Handle string predicates
    if isinstance(predicate, str):
        predicate_lower = predicate.lower()
        if predicate_lower in ["intersects", "intersect"]:
            return cell_polygon.intersects(input_geometry)
        elif predicate_lower == "within":
            return cell_polygon.within(input_geometry)
        elif predicate_lower in ["centroid_within", "centroid"]:
            return cell_polygon.centroid.within(input_geometry)
        elif predicate_lower in ["largest_overlap", "overlap", "majority"]:
            # intersection >= 50% of cell area
            if cell_polygon.intersects(input_geometry):
                intersection_geom = cell_polygon.intersection(input_geometry)
                if intersection_geom and intersection_geom.area > 0:
                    intersection_area = intersection_geom.area
                    cell_area = cell_polygon.area
                    return (intersection_area / cell_area) >= 0.5
            return False
        else:
            # Unknown string predicate, default to intersects
            return cell_polygon.intersects(input_geometry)

    # Handle integer predicates (backward compatibility)
    elif isinstance(predicate, int):
        if predicate == 0:
            # Default: intersects
            return cell_polygon.intersects(input_geometry)
        elif predicate == 1:
            # within
            return cell_polygon.within(input_geometry)
        elif predicate == 2:
            # centroid_within
            return cell_polygon.centroid.within(input_geometry)
        elif predicate == 3:
            # intersection >= 50% of cell area
            if cell_polygon.intersects(input_geometry):
                intersection_geom = cell_polygon.intersection(input_geometry)
                if intersection_geom and intersection_geom.area > 0:
                    intersection_area = intersection_geom.area
                    cell_area = cell_polygon.area
                    return (intersection_area / cell_area) >= 0.5
            return False
        else:
            # Unknown predicate, default to intersects
            return cell_polygon.intersects(input_geometry)

    else:
        # None or other types, default to intersects
        return cell_polygon.intersects(input_geometry)


def check_crossing(lon1: float, lon2: float, validate: bool = True):
    """
    Assuming a minimum travel distance between two provided longitude coordinates,
    checks if the 180th meridian (antimeridian) is crossed.
    """
    if validate and any(abs(x) > 180.0 for x in [lon1, lon2]):
        raise ValueError("longitudes must be in degrees [-180.0, 180.0]")
    return abs(lon2 - lon1) > 180.0


def check_crossing_geom(geom):
    """
    Check if a geometry crosses the antimeridian (180th meridian).

    Args:
        geom: Shapely geometry (Polygon, MultiPolygon)

    Returns:
        bool: True if any part of the geometry crosses the antimeridian, False otherwise
    """
    crossed = False
    try:
        # Handle None or empty geometries
        if geom is None or geom.is_empty:
            return False

        # Handle multi-geometries
        if hasattr(geom, "geoms"):
            # MultiPolygon
            for sub_geom in geom.geoms:
                if check_crossing_geom(sub_geom):
                    crossed = True
                    break
            return crossed

        # Handle single Polygon
        if geom.geom_type == "Polygon":
            # Check if exterior has coordinates
            if geom.exterior is None or len(geom.exterior.coords) == 0:
                return False

            # Check exterior ring only
            p_init = geom.exterior.coords[0]
            for p in range(1, len(geom.exterior.coords)):
                px = geom.exterior.coords[p]
                try:
                    if check_crossing(p_init[0], px[0]):
                        crossed = True
                        break
                except ValueError:
                    crossed = True
                    break
                p_init = px
    except Exception:
        return False

    return crossed


def dggal_to_geo(dggs_type: str, zone_id: str, options: dict = {}):
    """
    Convert a DGGAL ZoneID to a Shapely Polygon.

    Args:
        dggs_type (str): The DGGS type e.g 'gnosis','isea4r','isea9r','isea3h','isea7h','isea7h_z7',
            'ivea4r','ivea9r','ivea3h','ivea7h','ivea7h_z7','rtea4r','rtea9r','rtea3h','rtea7h','rtea7h_z7','healpix','rhealpix'
        zone_id (str): The zone identifier
        options (dict): Options for geometry generation
            - 'crs' (str | None): "5x6" or "isea" to select alternate CRS; default WGS84

    Returns:
        shapely.geometry.Polygon: Shapely Polygon or None if invalid zone
    """
    # Validate DGGS type
    dggs_type = validate_dggal_type(dggs_type)
    # Create the appropriate DGGS instance
    dggs_class_name = DGGAL_TYPES[dggs_type]["class_name"]
    dggrs = globals()[dggs_class_name]()

    # Get zone
    zone = dggrs.getZoneFromTextID(zone_id)
    if zone == nullZone:
        return None

    # Get CRS option
    crsOption = options.get("crs") if options else None
    crs = 0

    if crsOption:
        if crsOption == "5x6":
            crs = CRS(ogc, 153456)
        elif crsOption == "isea":
            crs = CRS(ogc, 1534)

    # Get vertices based on CRS
    if not crs or crs == CRS(ogc, 84) or crs == CRS(epsg, 4326):
        vertices = dggrs.getZoneRefinedWGS84Vertices(zone, 0)
        if vertices and vertices.count:
            count = vertices.count
            # Create list of (lon, lat) coordinates
            coords = [
                (float(vertices[i].lon), float(vertices[i].lat)) for i in range(count)
            ]
            # Close the polygon by adding the first point at the end
            coords.append(coords[0])
            return shapely.geometry.Polygon(coords)
    else:
        vertices = dggrs.getZoneRefinedCRSVertices(zone, crs, 0)
        if vertices and vertices.count:
            count = vertices.count
            # Create list of (x, y) coordinates
            coords = [
                (float(vertices[i].x), float(vertices[i].y)) for i in range(count)
            ]
            # Close the polygon by adding the first point at the end
            coords.append(coords[0])
            return shapely.geometry.Polygon(coords)

    # Return None if no valid vertices found
    return None


def dggal_dggsjsonfile2geojson(input_file, output_file=None, options: dict = {}):
   exitCode = 1
   try:
      # Check if input is a URL
      parsed_url = urlparse(input_file)
      is_url_input = all([parsed_url.scheme, parsed_url.netloc])
      
      # Read the JSON file from URL or local file
      if is_url_input:
         try:
            response = requests.get(input_file)
            response.raise_for_status()
            dggal_json = response.json()
         except requests.RequestException as e:
            print(f"Failure to download file from URL {input_file}: {str(e)}")
            return exitCode
      else:
         # Read from local file
         with open(input_file, 'r', encoding='utf-8') as f:
            dggal_json = json.load(f)
      
      if dggal_json:
         # Extract options
         centroids = options.get('centroids') if options else False
         crsOption = options.get('crs') if options else None
         crs = None

         # Convert CRS option string to CRS object
         if crsOption:
            if crsOption == "5x6":
               crs = CRS(ogc, 153456)
            elif crsOption == "isea":
               crs = CRS(ogc, 1534)

         # Use dggal_dggsjson2geojson to convert
         geojson_result = dggal_dggsjson2geojson(dggal_json, crs=crs, centroids=centroids)
         
         if geojson_result:
            # Generate output filename: <input file name>.geojson
            if is_url_input:
               # Extract filename from URL path
               url_path = parsed_url.path.rstrip('/')
               if url_path:
                  input_basename = os.path.splitext(os.path.basename(url_path))[0]
                  # If no filename in URL path, use domain name
                  if not input_basename:
                     input_basename = parsed_url.netloc.replace('.', '_') if parsed_url.netloc else 'output'
               else:
                  # No path in URL, use domain name
                  input_basename = parsed_url.netloc.replace('.', '_') if parsed_url.netloc else 'output'
            else:
               # Local file: use the basename without extension
               input_basename = os.path.splitext(os.path.basename(input_file))[0]
            
            if output_file is None:
                output_file = os.path.join(os.getcwd(), f"{input_basename}.geojson")
            
            # Write GeoJSON to file
            with open(output_file, 'w', encoding='utf-8') as f:
               json.dump(geojson_result, f, indent=2)
            
            exitCode = 0
         else:
            print(f"Failed to convert DGGS-JSON to GeoJSON")
      else:
         print(f"Failure to parse DGGS-JSON file {input_file}")
   except FileNotFoundError:
      print(f"Failure to open file {input_file}")
   except json.JSONDecodeError as e:
      print(f"Failure to parse DGGS-JSON file {input_file}: {str(e)}")
   except Exception as e:
      print(f"Error processing file {input_file}: {str(e)}")
   
   return exitCode


def dggal_generatezonegeometry(dggrs, zone, crs, id, centroids: bool, fc: bool):
   coordinates = []
   if not crs or crs == CRS(ogc, 84) or crs == CRS(epsg, 4326):
      if centroids:
         centroid = dggrs.getZoneWGS84Centroid(zone, centroid)
         coordinates.append(centroid.lon.value)
         coordinates.append(centroid.lat.value)
      else:
         vertices = dggrs.getZoneRefinedWGS84Vertices(zone, 0)
         if vertices:
            contour = [ ]
            for v in vertices:
               contour.append([ v.lon.value, v.lat.value])
            contour.append([vertices[0].lon.value, vertices[0].lat.value])
            coordinates.append(contour)
   else:
      if centroids:
         centroid = dggrs.getZoneCRSCentroid(zone, crs, centroid)
         coordinates.append(centroid.x)
         coordinates.append(centroid.y)
      else:
         vertices = dggrs.getZoneRefinedCRSVertices(zone, crs, 0)
         if vertices:
            count = vertices.count
            contour = [ ]
            for v in vertices:
               contour.append([v.x, v.y])
            contour.append([vertices[0].x, vertices[0].y])
            coordinates.append(contour)
   geometry = {
      'type': 'Point' if centroids else 'Polygon',
      'coordinates': coordinates
   }
   return geometry

def dggal_generatezonefeature(dggrs, zone, crs, id, centroids: bool, fc: bool, props):
   zoneID = dggrs.getZoneTextID(zone)

   properties = {
      'zoneID': f'{zoneID}'
   }
   if props:
      for key, v in props.items():
         properties[key] = v

   features = {
      'type': 'Feature',
      'id': id if id is not None else zoneID,
      'geometry': dggal_generatezonegeometry(dggrs, zone, crs, id, centroids, fc),
      'properties': properties
   }
   return features

def dggal_dggsjson2geojson(dggal_json, crs: CRS = None, centroids: bool = False):
   result = None
   if dggal_json is not None:
         dggrsClass = None
         dggrsID = getLastDirectory(dggal_json['dggrs'])

         # We could use globals()['GNOSISGlobalGrid'] to be more generic, but here we limit to DGGRSs we know
         if   not strnicmp(dggrsID, "GNOSIS", 6): dggrsClass = GNOSISGlobalGrid
         elif not strnicmp(dggrsID, "ISEA4R", 6): dggrsClass = ISEA4R
         elif not strnicmp(dggrsID, "ISEA9R", 6): dggrsClass = ISEA9R
         elif not strnicmp(dggrsID, "ISEA3H", 6): dggrsClass = ISEA3H
         elif not strnicmp(dggrsID, "ISEA7H", 6): dggrsClass = ISEA7H
         elif not strnicmp(dggrsID, "IVEA4R", 6): dggrsClass = IVEA4R
         elif not strnicmp(dggrsID, "IVEA9R", 6): dggrsClass = IVEA9R
         elif not strnicmp(dggrsID, "IVEA3H", 6): dggrsClass = IVEA3H
         elif not strnicmp(dggrsID, "IVEA7H", 6): dggrsClass = IVEA7H
         elif not strnicmp(dggrsID, "RTEA4R", 6): dggrsClass = RTEA4R
         elif not strnicmp(dggrsID, "RTEA9R", 6): dggrsClass = RTEA9R
         elif not strnicmp(dggrsID, "RTEA3H", 6): dggrsClass = RTEA3H
         elif not strnicmp(dggrsID, "RTEA7H", 6): dggrsClass = RTEA7H
         elif not strnicmp(dggrsID, "HEALPix", 7): dggrsClass = HEALPix
         elif not strnicmp(dggrsID, "rHEALPix", 8): dggrsClass = rHEALPix

         if dggrsClass:
            zoneID = dggal_json['zoneId']
            dggrs = dggrsClass()
            zone = dggrs.getZoneFromTextID(zoneID)

            if zone != nullZone:
                depths = dggal_json['depths']
                if depths:
                  maxDepth = -1

                  for d in range(len(depths)):
                     depth = depths[d]
                     if depth > maxDepth:
                        maxDepth = depth
                        break;
                  if d < len(depths):
                     depth = maxDepth
                     subZones = dggrs.getSubZones(zone, depth)
                     if subZones:
                        i = 0
                        values = dggal_json['values']
                        features = [ ]
                        for z in subZones:
                           props = { }

                           # NOTE: We should eventually try to support __iter__ on containers
                           #       for key, depths in dggal_json.values.items():
                           for key, vDepths in values.items():
                              if key and vDepths and len(vDepths) > d:
                                 djDepth = vDepths[d]
                                 data = djDepth['data']
                                 props[key] = data[i]

                           features.append(dggal_generatezonefeature(dggrs, z, crs, i + 1, centroids, True, props))
                           i += 1
                        result = {
                           'type': 'FeatureCollection',
                           'features': features
                        }
   return result

def characteristic_length_scale(
    cell_area: float, unit: str = "m"
):  # cell_area is in m2
    """
    Compute the Characteristic Length Scale (CLS) from the cell area.

    Parameters
    ----------
    cell_area : float
        Cell area in m²

    Returns
    -------
    float
        Characteristic length scale in the m
    """
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")
    # average cell area (always in m²)
    # cell_area = 4 * math.pi * AUTHALIC_RADIUS**2 / (N_cells)
    term = math.sqrt(cell_area / math.pi) / (2.0 * AUTHALIC_RADIUS)

    # Handle case where term > 1 (can happen with very small cell areas)
    # This indicates the cell is smaller than what can be represented on the sphere
    if term > 1:
        # Return a very small value as the characteristic length scale
        # This is the maximum possible CLS (half the circumference of the Earth)
        cls = 2.0 * math.pi * AUTHALIC_RADIUS
    else:
        cls = 4.0 * AUTHALIC_RADIUS * math.asin(term)
    if unit == "km":
        cls = cls / (10**3)
    return cls


def characteristic_length_scale_from_num_cells(N_cells: int, unit: str = "m"):
    """
    Compute the Characteristic Length Scale (CLS) from the number of cells.

    Parameters
    ----------
    N_cells : int
        Number of cells at the given resolution.

    Returns
    -------
    float
        Characteristic length scale in m

    """
    # Validate unit parameter
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")

    # average cell area (always in m²)
    cell_area = 4 * math.pi * AUTHALIC_RADIUS**2 / (N_cells)
    term = math.sqrt(cell_area / math.pi) / (2.0 * AUTHALIC_RADIUS)

    # Handle case where term > 1 (can happen with very large numbers of cells)
    # This indicates the cell is smaller than what can be represented on the sphere
    if term > 1:
        # Return a very small value as the characteristic length scale
        # This is the maximum possible CLS (half the circumference of the Earth)
        cls = 2.0 * math.pi * AUTHALIC_RADIUS
    else:
        cls = 4.0 * AUTHALIC_RADIUS * math.asin(term)

    if unit == "km":
        cls = cls / (10**3)
    return cls


def dggrid_intercell_distance(dggs_type: str, resolution: int, unit: str = "m"):
    """
    Compute the intercell distance in meters for a given DGGRID type and resolution.
    """
    dggs_type = validate_dggrid_type(dggs_type)
    intercell_dist = ICOSA_EDGE_M
    aperture = 4
    if dggs_type in ["ISEA4T", "FULLER4T"]:
        intercell_dist /= math.sqrt(3)
    elif dggs_type in ["ISEA3H", "FULLER3H"]:
        aperture = 3
    elif dggs_type in [
        "ISEA4T",
        "ISEA4D",
        "ISEA4H",
        "FULLER4T",
        "FULLER4D",
        "FULLER4H",
    ]:
        aperture = 4
    elif dggs_type in ["ISEA7H", "FULLER7H", "IGEO7", "PLANETRISK"]:
        aperture = 7
    elif dggs_type in ["PLANETRISK"]:  # Resolution pattern: _43334777777777777777777
        if resolution == 1 or resolution == 5:
            aperture = 4
        elif resolution > 1 and resolution < 5:
            aperture = 3
        else:
            aperture = 7
    else:
        return None

    intercell_dist /= pow(math.sqrt(aperture), resolution)
    if unit == "km":
        intercell_dist = intercell_dist / (10**3)

    return intercell_dist

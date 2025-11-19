"""
Export a city into STL format with surface-to-triangle mapping
SPDX-License-Identifier: LGPL-3.0-or-later
Copyright © 2022 Concordia CERC group
Project Coder Guille Gutierrez guillermo.gutierrezmorote@concordia.ca
Modified by Saeed Rayegan
"""
from pathlib import Path
import numpy as np
import json
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.ops import polygonize


class Stl:
  """
  Export to STL format with a mapping of triangles to parent surface IDs
  """
  def __init__(self, city, path, height_axis='z'):
    self._city = city
    self._path = path
    self._height_axis = height_axis.lower()
    if self._height_axis not in ['y', 'z']:
      raise ValueError("height_axis must be 'y' or 'z'")
    self._export()

  def _ground(self, coordinate):
    """
    Transform coordinates relative to the city's lower corner
    """
    x = coordinate[0] - self._city.lower_corner[0]
    y = coordinate[1] - self._city.lower_corner[1]
    z = coordinate[2] - self._city.lower_corner[2]
    return x, y, z

  def _calculate_normal(self, coordinates):
    """
    Calculate the normal vector for a set of coordinates (assumes planar polygon)
    """
    ground_vertex = [np.array(self._ground(coord)) for coord in coordinates]
    edge_1 = ground_vertex[1] - ground_vertex[0]
    edge_2 = ground_vertex[2] - ground_vertex[0]
    normal = np.cross(edge_1, edge_2)
    normal = normal / np.linalg.norm(normal)
    return normal

  def _point_in_triangle(self, pt, tri):
    """
    Check if a point is inside a triangle using barycentric coordinates
    """
    ax, ay = tri[0]
    bx, by = tri[1]
    cx, cy = tri[2]
    px, py = pt
    denom = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(denom) < 1e-6:
      return False
    alpha = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / denom
    beta = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / denom
    gamma = 1 - alpha - beta
    return 0 <= alpha <= 1 and 0 <= beta <= 1 and 0 <= gamma <= 1

  def _triangulate_polygon(self, coords):
    """
    Triangulate a 2D polygon using ear clipping algorithm
    """
    if len(coords) < 3:
      return []
    vertices = list(range(len(coords)))
    triangles = []
    while len(vertices) > 3:
      ear_found = False
      n = len(vertices)
      i = 0
      while i < n:
        prev_i = (i - 1) % n
        curr_i = i
        next_i = (i + 1) % n
        p_prev = coords[vertices[prev_i]]
        p_curr = coords[vertices[curr_i]]
        p_next = coords[vertices[next_i]]
        v1 = (p_curr[0] - p_prev[0], p_curr[1] - p_prev[1])
        v2 = (p_next[0] - p_curr[0], p_next[1] - p_curr[1])
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        if cross <= 0:
          i += 1
          continue  # Not a convex vertex
        # Check if any point is inside the triangle
        is_ear = True
        for j in range(n):
          if vertices[j] in (vertices[prev_i], vertices[curr_i], vertices[next_i]):
            continue
          if self._point_in_triangle(coords[vertices[j]], [p_prev, p_curr, p_next]):
            is_ear = False
            break
        if is_ear:
          triangles.append([p_prev, p_curr, p_next])
          del vertices[curr_i]
          ear_found = True
          break
        i += 1
      if not ear_found:
        break  # Unable to find an ear, polygon may be invalid
    if len(vertices) == 3:
      triangles.append([coords[vertices[0]], coords[vertices[1]], coords[vertices[2]]])
    return triangles

  def _collect_footprint(self, building):
    """
    Collect building footprint from bottom edges of wall surfaces (projected on XY plane).
    Assembles edges into a polygon using polygonize.
    Returns ordered list of (x, y).
    """
    footprint_edges = []
    for tz in building.thermal_zones_from_internal_zones:
      for boundary in tz.thermal_boundaries:
        surface = boundary.parent_surface
        if surface.type != 'Wall':
          continue
        coords = surface.solid_polygon.coordinates
        ground_coords = [self._ground(c) for c in coords]
        zs = [c[2] for c in ground_coords]
        if not zs:
          continue
        min_z = min(zs)
        bottom_points = [(c[0], c[1]) for c in ground_coords if abs(c[2] - min_z) < 1e-6]
        unique_bottom = set(bottom_points)  # Remove duplicates
        if len(unique_bottom) == 2:
          p1, p2 = list(unique_bottom)
          footprint_edges.append(LineString([p1, p2]))

    if not footprint_edges:
      return []

    multilines = MultiLineString(footprint_edges)
    result = polygonize(multilines)
    polygons = [geom for geom in result if geom.geom_type == 'Polygon']  # Updated line
    if not polygons:
      return []
    # Select the largest polygon (assuming it's the outer footprint)
    main_poly = max(polygons, key=lambda p: p.area)
    footprint = list(main_poly.exterior.coords)[:-1]

    # Ensure counterclockwise orientation
    area = sum(footprint[i][0] * footprint[(i + 1) % len(footprint)][1] -
               footprint[(i + 1) % len(footprint)][0] * footprint[i][1]
               for i in range(len(footprint))) / 2.0
    if area < 0:
      footprint = footprint[::-1]

    return footprint

  def _triangulate(self, coordinates, surface_type, building=None):
    """
    Triangulate polygons into triangles.
    For Roof and Ground, rebuild polygons from footprint and set z levels.
    """
    triangles = []

    if surface_type in ['Roof', 'Ground'] and building is not None:
      footprint = self._collect_footprint(building)
      if len(footprint) < 3:
        return [], 0

      if surface_type == 'Ground':
        z_level = 0.0
      else:  # Roof
        # Max Z of building surfaces
        all_z = [
          self._ground(coord)[2]
          for tz in building.thermal_zones_from_internal_zones
          for b in tz.thermal_boundaries
          for coord in b.parent_surface.solid_polygon.coordinates
        ]
        z_level = max(all_z) if all_z else 0.0

      triangles_2d = self._triangulate_polygon(footprint)
      triangles = [[(p[0], p[1], z_level) for p in tri] for tri in triangles_2d]
      return triangles, len(triangles)

    # Default triangulation for walls and other surfaces (assuming quad or tri)
    ground_coords = [self._ground(coord) for coord in coordinates]
    if len(ground_coords) >= 4:
      triangles.append([ground_coords[0], ground_coords[1], ground_coords[2]])
      triangles.append([ground_coords[0], ground_coords[2], ground_coords[3]])
    elif len(ground_coords) == 3:
      triangles.append([ground_coords[0], ground_coords[1], ground_coords[2]])
    return triangles, len(triangles)

  def _export(self):
    """
    Export city geometry to STL ASCII format and create a surface-to-triangle mapping
    """
    if self._city.name is None:
      self._city.name = 'unknown_city'
    stl_name = f'{self._city.name}.stl'
    mapping_name = f'{self._city.name}_surface_mapping.json'
    stl_file_path = (Path(self._path).resolve() / stl_name).resolve()
    mapping_file_path = (Path(self._path).resolve() / mapping_name).resolve()

    mapping = {
      "facets": [],  # List of {facet_index, surface_id}
      "surface_triangle_counts": {}  # Dict of surface_id: triangle_count
    }
    facet_index = 0

    with open(stl_file_path, 'w', encoding='utf-8') as stl:
      for building in self._city.buildings:
        stl.write(f"solid {building.name}\n")

        for storey, thermal_zone in enumerate(building.thermal_zones_from_internal_zones):
          for index, boundary in enumerate(thermal_zone.thermal_boundaries):
            surface_id = f"BUILDING_{building.name.upper()}_STOREY_{storey}_SURFACE_{index}"
            surface = boundary.parent_surface

            # Use roof/ground reconstruction if needed
            triangles, triangle_count = self._triangulate(
              surface.solid_polygon.coordinates, surface.type, building=building
            )
            if triangle_count == 0:
              continue

            # Normal: use first triangle for consistency
            normal = self._calculate_normal(triangles[0])

            mapping["surface_triangle_counts"][surface_id] = triangle_count
            for _ in range(triangle_count):
              mapping["facets"].append({"facet_index": facet_index, "surface_id": surface_id})
              facet_index += 1

            # Write STL triangles
            for triangle in triangles:
              if self._height_axis == "z":
                stl.write(f"  facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n")
              elif self._height_axis == "y":
                stl.write(f"  facet normal {normal[0]:.6f} {normal[2]:.6f} {normal[1]:.6f}\n")
              stl.write("    outer loop\n")
              for vertex in triangle:
                if self._height_axis == "z":
                  stl.write(f"      vertex {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
                elif self._height_axis == "y":
                  stl.write(f"      vertex {vertex[0]:.6f} {vertex[2]:.6f} {vertex[1]:.6f}\n")
              stl.write("    endloop\n")
              stl.write("  endfacet\n")

        stl.write(f"endsolid {building.name}\n")

    with open(mapping_file_path, 'w', encoding='utf-8') as f:
      json.dump(mapping, f, indent=2)
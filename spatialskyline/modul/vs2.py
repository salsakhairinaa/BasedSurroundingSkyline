# Modul Skyline Voronoi-based Spatial Skyline (VS2)

import numpy as np
import pandas as pd
import heapq
from scipy.spatial import ConvexHull, convex_hull_plot_2d
from scipy.spatial import Voronoi, voronoi_plot_2d, distance
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

#### Fungsi voronoi_finite_polygons_2d
# Fungsi mendapatkan voronoi cell finite (rekonstruksi voronoi diagram agar tidak ada voronoi cell yang infinite.
# Kode program dari: https://gist.github.com/pv/8036995)
def voronoi_finite_polygons_2d(vor, radius=None):
    # """
    # Reconstruct infinite voronoi regions in a 2D diagram to finite
    # regions.
    # Parameters
    # ----------
    # vor : Voronoi
    #     Input diagram
    # radius : float, optional
    #     Distance to 'points at infinity'.
    # Returns
    # -------
    # regions : list of tuples
    #     Indices of vertices in each revised Voronoi regions.
    # vertices : list of tuples
    #     Coordinates for revised Voronoi vertices. Same as coordinates
    #     of input vertices, with 'points at infinity' appended to the
    #     end.
    # """

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()*2

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1] # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)

#### Fungsi MBR
# Fungsi membuat MBR (Minimum Bounding Rectangle) dari circle antara *p* dengan vertex dari convexhull *q*
def MBR(idx_point, dist_poi, hull_vertices):

    kiri = [hull_vertices[i][0]-dist_poi[idx_point][i] for i in range(0, len(hull_vertices))]
    kanan = [hull_vertices[i][0]+dist_poi[idx_point][i] for i in range(0, len(hull_vertices))]
    atas = [hull_vertices[i][1]+dist_poi[idx_point][i] for i in range(0, len(hull_vertices))]
    bawah = [hull_vertices[i][1]-dist_poi[idx_point][i] for i in range(0, len(hull_vertices))]

    kiri_atas, kiri_bawah = np.array([min(kiri), max(atas)]), np.array([min(kiri), min(bawah)])
    kanan_bawah, kanan_atas = np.array([max(kanan), min(bawah)]), np.array([max(kanan), max(atas)])

    mbr = Polygon([kiri_atas, kiri_bawah, kanan_bawah, kanan_atas])

    return mbr

#### Fungsi is_dominated
# Fungsi melakukan pengecekan terhadap suatu point apakah point tersebut didominasi atau
# tidak oleh point-point yang ada di dalam skyline
def is_dominated(idx_point, dist_poi, hull_vertices, skyline):
    dominated = 'yes'
    sum_dominate = 0
    length = len(hull_vertices)
    dist_point_to_qpoint = dist_poi[idx_point]
    for sky in skyline:
        better = 0
        worse = 0
        equal = 0
        dist_sky_to_qpoint = dist_poi[sky]
        for i in range(0, length):
            if float(dist_point_to_qpoint[i]) < float(dist_sky_to_qpoint[i]):
                better += 1
            elif float(dist_point_to_qpoint[i]) > float(dist_sky_to_qpoint[i]):
                worse += 1
            else:
                equal += 1
        if better > 0 or equal == length:
            sum_dominate += 1
    if sum_dominate == len(skyline):
        dominated = 'no'

    return dominated

#### Fungsi voronoi_neighbors
# Fungsi memperoleh voronoi neighbor untuk semua point dalam voronoi diagram
def voronoi_neighbors(vor):
    all_neighbors = {}
    for (p1, p2) in vor.ridge_points:
        all_neighbors.setdefault(p1, []).append(p2)
        all_neighbors.setdefault(p2, []).append(p1)

    return all_neighbors

#### Fungsi vorn_in_skyline
# Fungsi mengecek apakah voronoi neighbor suatu point terdapat dalam skyline atau tidak
def vorn_in_skyline(vorn_p, skyline):
    in_skyline = 'no'
    for vorn in vorn_p:
        if vorn in skyline:
            in_skyline = 'yes'
            break

    return in_skyline

#### Fungsi mindist
# Fungsi menghitung mindist untuk semua point (sum distance dari point ke query point)
def mindist(idx_point, dist_poi):
    total = sum(dist_poi[idx_point])

    return total

#### Fungsi get_skyline_vs2
# Fungsi utama yang menjalankan fungsi lainnya.
# Parameter yang dibutuhkan yaitu data poi (point) dan juga data query (query point)
def get_skyline_vs2(poi_awal, query_awal, rating=0):
    data_poi = poi_awal[poi_awal['rating'] >= float(rating)]
    if len(data_poi) < 2:
        return data_poi
    else:
        poi = data_poi[['latitude', 'longitude']].values.tolist()
        poi = np.array(poi)

        query = query_awal[['latitude', 'longitude']].values.tolist()
        query = np.array(query)

        skyline = []
        minheap = []
        visited = []
        extracted = []

        vor = Voronoi(poi)
        regions, vertices = voronoi_finite_polygons_2d(vor)

        if len(query_awal)==2:
            vor = Voronoi(poi)
            hull_vertices = [que for que in query]

        else:
            hull = ConvexHull(query)
            hull_vertices = [query[i] for i in hull.vertices]
            ch = Polygon(hull_vertices)

        dist_poi = distance.cdist(poi, hull_vertices, 'euclidean')
        nn = np.where(dist_poi[:,0] == min(dist_poi[:,0]))[0][0]

        mindist_nn = mindist(nn, dist_poi)
        heapq.heappush(minheap, (mindist_nn, nn))
        visited.append(nn)

        MBR_nn = MBR(nn, dist_poi, hull_vertices)
        B = MBR_nn
        vor_neighbors = voronoi_neighbors(vor)

        vor_ver = []
        for region in regions:
            vor_ver.append(vertices[region])

        while minheap:
            key, p = minheap[0]
            a = np.array(minheap)
            if p in extracted:
                heapq.heappop(minheap)
                p_is_dominated_by_skyline = is_dominated(p, dist_poi, hull_vertices, skyline)
                if len(query_awal)==2:
                    if p_is_dominated_by_skyline == 'no':
                        skyline.append(p)
                else:
                    if Point(poi[p]).within(ch) or p_is_dominated_by_skyline == 'no':
                        skyline.append(p)
            else:
                extracted.append(p)
                vorn_p = vor_neighbors[p]
                vorn_p_in_skyline = vorn_in_skyline(vorn_p, skyline)
                if not skyline or vorn_p_in_skyline == 'yes':
                    for p_ in vorn_p:
                        if p_ in visited:
                            continue
                        elif Point(poi[p_]).within(B)  or Polygon(vor_ver[p_]).intersects(B):
                            visited.append(p_)
                            mindist_p_ = mindist(p_, dist_poi)
                            heapq.heappush(minheap, (mindist_p_, p_))
                            MBR_p_ = MBR(p_, dist_poi, hull_vertices)
                            B = B.intersection(MBR_p_)

        return data_poi.iloc[skyline].sort_index()

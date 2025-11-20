# =====
# GRAX
# =====



# Import Libraries
import fiona
import networkx as nx
from shapely.geometry import LineString
import numpy as np



""" Define GRAX Library """
class grax:
    """
    Build a NetworkX graph from polyline-like data (e.g., from shapefiles).

    Parameters
    ----------
    verbose : int, optional (default=0)
        Verbosity level. 0 = silent, 1 = basic info.
    """



    # [1] Initialization Method
    def __init__(self, verbose: int = 0):
        self.verbose = verbose
        self.all_pt_mats_ = None
        self.graph_ = None



    # [2] Function to Convert Shape File into Matrices
    def digitize_shape(self, shapefile):
        """
        Digitize a shapefile into a set of matrices.

        Parameters
        ----------
        shapefile : shape file containing digitized elements (roads/watermains/gas pipes/etc)

        Returns
        -------
        all_point_matrices : list of numpy.ndarray
                             Each list element contains a numpy.ndarray describing: point id, x location, y location
        """
        
        # Create an empty list to store point matrices for each feature
        all_point_matrices = []

        # Open the shapefile using fiona
        with fiona.open(shapefile, "r") as source:
            
            # Iterate through features in the road layer
            for feature in source:
                # Get the geometry of the road segment
                geometry = feature["geometry"]

                # Extract all points' coordinates in the line segment
                points = geometry["coordinates"]
                
                # Create a matrix for the points with columns: point id, x location, y location
                point_matrix = np.array([(int(i + 1), point[0], point[1]) for i, point in enumerate(points)])

                # Add the point matrix to the list
                all_point_matrices.append(point_matrix)
        
        # Store for later inspection
        self.all_pt_mats_ = all_point_matrices

        return all_point_matrices



    # [3] Function to Create a Network from a Shape File
    def create_network(self, L):
        """
        Create a graph from a list/array of polylines.

        Parameters
        ----------
        L : list of numpy.ndarray
            Each element is an array of shape (n_points, 3) with: [node_id, x, y]

        Returns
        -------
        G : networkx.Graph
            Undirected graph with:
              - nodes: IDs like 'r_<line_id>_<node_id>' or 'is_i_j_k'
              - node attributes: x, y
              - edges: connectivity along lines + intersection splits
        """
        G = nx.Graph()
        Lst = L.copy()


        # Ensure object dtype (so we can insert strings for node IDs)
        for it in range(len(Lst)):
            Lst[it] = Lst[it].astype(object)

        g_line_id = 0


        # ------------------------------------
        # PART 1: Build nodes + edges per line
        # ------------------------------------
        for itm in range(len(Lst)):
            # Create undirected links within the same list item
            for i in range(len(Lst[itm])):
                node_id, x, y = Lst[itm][i]
                G.add_node(f'r_{g_line_id}_{node_id}', x=x, y=y)
                # Replace original node_id with the new prefixed one
                Lst[itm][i][0] = f'r_{g_line_id}_{node_id}'
            
            # Create edges between consecutive points along this line
            for j in range(len(Lst[itm])-1): 
                G.add_edge(Lst[itm][j][0], Lst[itm][j+1][0])
        
            g_line_id +=1


        # ------------------------------------
        # PART 2: Detect intersections
        # ------------------------------------
        for i in range(len(Lst) - 1):
            intersection_id = 0
            for j in range(i + 1, len(Lst)):

                # Extract coordinates for line segments
                item1_coords = [point[1:] for point in Lst[i]]  # [x, y]
                item2_coords = [point[1:] for point in Lst[j]]
                
                item1_coords_pointID = [point[0:1][0] for point in Lst[i]]
                item2_coords_pointID = [point[0:1][0] for point in Lst[j]]
                
                if self.verbose:
                    print(item1_coords_pointID)
                    print(item2_coords_pointID)

                # Check for intersections using shapely
                for i1 in range(len(item1_coords) - 1):
                    line1 = LineString(item1_coords[i1:i1+2])

                    for i2 in range(len(item2_coords) - 1):
                        line2 = LineString(item2_coords[i2:i2+2])
                        intersection = line1.intersection(line2)
                        
                        # Handle intersections
                        if not intersection.is_empty:
                            # For now we assume simple point intersections
                            intersect_x, intersect_y = intersection.x, intersection.y
                            intersect_node_id = f'is_{i}_{j}_{intersection_id}'
                            intersection_id +=1

                            # Add intersection node
                            G.add_node(intersect_node_id, x=intersect_x, y=intersect_y)

                            # --- FIRST LINE ---
                            # Connect intersection with neighboring nodes
                            G.add_edge(intersect_node_id, item1_coords_pointID[i1])
                            G.add_edge(intersect_node_id, item1_coords_pointID[i1+1])
                            
                            # Remove direct edge between neighbors (split by intersection)
                            if G.has_edge(item1_coords_pointID[i1], item1_coords_pointID[i1+1]):
                                G.remove_edge(item1_coords_pointID[i1], item1_coords_pointID[i1+1])
                            
                            # Insert the new node data at the specified index
                            Lst[i] = np.insert(
                                                Lst[i],
                                                i1+1,
                                                [intersect_node_id, intersect_x, intersect_y],
                                                axis=0
                                            )
                            
                            # --- SECOND LINE ---
                            # Add edges from intersection point to second line's neighboring points
                            G.add_edge(intersect_node_id, item2_coords_pointID[i2])
                            G.add_edge(intersect_node_id, item2_coords_pointID[i2+1])
                            
                            if G.has_edge(item2_coords_pointID[i2], item2_coords_pointID[i2+1]):
                                G.remove_edge(item2_coords_pointID[i2], item2_coords_pointID[i2+1])
                                
                            # Add the intersection point to the second line list
                            Lst[j] = np.insert(
                                                Lst[j],
                                                i2+1,
                                                [intersect_node_id, intersect_x, intersect_y],
                                                axis=0
                                            )
        
        # Store for later inspection
        self.graph_ = G

        return G
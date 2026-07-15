class _TriangleMesh:
    def __init__(self, *args, **kwargs):
        self.vertices = None
        self.triangles = None
    def compute_vertex_normals(self):
        return self
class _PointCloud:
    pass
class _Geometry:
    TriangleMesh = _TriangleMesh
    PointCloud = _PointCloud
class _Utility:
    @staticmethod
    def Vector3dVector(x): return x
    @staticmethod
    def Vector3iVector(x): return x
class _IO:
    @staticmethod
    def write_triangle_mesh(*args, **kwargs): return True
    @staticmethod
    def read_triangle_mesh(*args, **kwargs): return _TriangleMesh()
class _Visualization:
    @staticmethod
    def draw_geometries(*args, **kwargs): return None
geometry = _Geometry()
utility = _Utility()
io = _IO()
visualization = _Visualization()

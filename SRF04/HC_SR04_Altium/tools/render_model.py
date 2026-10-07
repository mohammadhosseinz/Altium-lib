"""Render the supplied STEP in its footprint orientation.

Requires cadquery-ocp-novtk==7.9.3.1.1, numpy and Pillow. Colors are illustrative.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID, TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location

ROOT = Path(__file__).resolve().parents[1]


def render():
    reader = STEPControl_Reader()
    assert reader.ReadFile(str(ROOT / '3D/HC_SR04.step')) == IFSelect_RetDone
    reader.TransferRoots()
    shape = reader.OneShape()
    BRepMesh_IncrementalMesh(shape, 0.12, False, 0.25, True).Perform()
    # Camera from front (-Y), slightly to the right and above.
    eye = np.array([0.42, -0.85, 0.48]); eye /= np.linalg.norm(eye)
    right = np.cross([0, 0, 1], eye); right /= np.linalg.norm(right)
    up = np.cross(eye, right)
    camera = np.stack([right, up, eye])
    faces = []
    solids = TopExp_Explorer(shape, TopAbs_SOLID)
    while solids.More():
        solid = solids.Current()
        vertices = []
        local_faces = []
        exp = TopExp_Explorer(solid, TopAbs_FACE)
        while exp.More():
            face = TopoDS.Face_s(exp.Current())
            loc = TopLoc_Location()
            mesh = BRep_Tool.Triangulation_s(face, loc)
            if mesh is not None:
                pts = []
                for i in range(1, mesh.NbNodes() + 1):
                    p = mesh.Node(i).Transformed(loc.Transformation())
                    # Same Rx90 / Y translation as the saved PCB body.
                    pts.append([p.X(), -p.Z() - 10.05, p.Y()])
                pts = np.asarray(pts)
                vertices.extend(pts)
                for i in range(1, mesh.NbTriangles() + 1):
                    inds = list(mesh.Triangle(i).Get())
                    if face.Orientation() == TopAbs_REVERSED: inds.reverse()
                    local_faces.append(pts[np.array(inds) - 1])
            exp.Next()
        bounds = np.ptp(np.asarray(vertices), axis=0)
        if bounds[0] > 40: color = np.array([35, 107, 165])  # module board
        elif bounds[0] < 1: color = np.array([206, 172, 77])  # header contacts
        elif bounds[0] < 11: color = np.array([40, 46, 57])  # plastic / small component
        else: color = np.array([187, 197, 208])  # transducers
        for tri in local_faces:
            normal = np.cross(tri[1] - tri[0], tri[2] - tri[0])
            length = np.linalg.norm(normal)
            if length < 1e-9: continue
            light = np.array([-0.3, -0.65, 0.7]); light /= np.linalg.norm(light)
            shade = 0.45 + 0.55 * abs(float(np.dot(normal / length, light)))
            faces.append((tri @ camera.T, tuple((color * shade).astype(int))))
        solids.Next()
    points = np.concatenate([t for t, _ in faces])
    low, high = points.min(axis=0), points.max(axis=0)
    width, height = 1440, 1060
    scale = min((width - 180) / (high[0] - low[0]), (height - 260) / (high[1] - low[1]))
    center = (low + high) / 2
    im = Image.new('RGB', (width, height), '#f3f6fa')
    pixels = np.array(im)
    depth = np.full((height, width), -np.inf)
    # Per-pixel depth avoids painter artifacts on overlapping curved surfaces.
    for tri, color in faces:
        xy = np.column_stack([width/2 + (tri[:, 0]-center[0])*scale,
                              height/2 + 30 - (tri[:, 1]-center[1])*scale])
        left, top = np.maximum(np.floor(xy.min(axis=0)).astype(int), [0, 0])
        right_bound, bottom = np.minimum(np.ceil(xy.max(axis=0)).astype(int), [width-1, height-1])
        if left > right_bound or top > bottom: continue
        x, y = np.meshgrid(np.arange(left, right_bound+1)+0.5, np.arange(top, bottom+1)+0.5)
        a, b, c = xy
        denom = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
        if abs(denom) < 1e-9: continue
        wa = ((b[1]-c[1])*(x-c[0]) + (c[0]-b[0])*(y-c[1])) / denom
        wb = ((c[1]-a[1])*(x-c[0]) + (a[0]-c[0])*(y-c[1])) / denom
        wc = 1-wa-wb
        z = wa*tri[0, 2] + wb*tri[1, 2] + wc*tri[2, 2]
        window = depth[top:bottom+1, left:right_bound+1]
        visible = (wa >= -1e-7) & (wb >= -1e-7) & (wc >= -1e-7) & (z > window)
        window[visible] = z[visible]
        pixels[top:bottom+1, left:right_bound+1][visible] = color
    im = Image.fromarray(pixels)
    draw = ImageDraw.Draw(im)
    try:
        title = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 46)
        font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 25)
    except OSError:
        title = font = ImageFont.load_default()
    draw.text((65, 35), 'HC-SR04', fill='#182c45', font=title)
    draw.text((65, 100), 'Supplied STEP geometry | Vertical right-angle-header mounting', fill='#4c6078', font=font)
    draw.text((65, height-75), '45 x 20 mm module PCB | 2.54 mm pin pitch | Illustrative materials', fill='#4c6078', font=font)
    im.save(ROOT / '3D/Preview.png')
    print(f'Rendered {len(faces)} CAD triangles')


if __name__ == '__main__': render()

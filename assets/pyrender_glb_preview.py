import argparse
import math
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
import pyrender
import trimesh


def add_meshes(scene: pyrender.Scene, src: trimesh.Scene | trimesh.Trimesh):
    if isinstance(src, trimesh.Trimesh):
        meshes = [(src, np.eye(4))]
        bounds = src.bounds
    else:
        meshes = []
        for name, geom in src.geometry.items():
            transform = src.graph.get(name)[0]
            meshes.append((geom, transform))
        bounds = src.bounds

    center = bounds.mean(axis=0)
    extent = max(float((bounds[1] - bounds[0]).max()), 1e-6)
    norm = np.eye(4)
    norm[:3, :3] *= 3.0 / extent
    norm[:3, 3] = -center * (3.0 / extent)

    for geom, transform in meshes:
        if not isinstance(geom, trimesh.Trimesh) or len(geom.vertices) == 0:
            continue
        mesh = geom.copy()
        mesh.apply_transform(norm @ transform)
        scene.add(pyrender.Mesh.from_trimesh(mesh, smooth=True))


def look_at(camera_pos, target=(0.0, 0.0, 0.0)):
    camera_pos = np.asarray(camera_pos, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    forward = target - camera_pos
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, np.array([0.0, 0.0, 1.0]))
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    pose = np.eye(4)
    pose[:3, 0] = right
    pose[:3, 1] = up
    pose[:3, 2] = -forward
    pose[:3, 3] = camera_pos
    return pose


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--glb", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--size", type=int, default=1200)
    parser.add_argument("--view", choices=["iso", "front", "side"], default="iso")
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    loaded = trimesh.load(str(args.glb), force="scene", process=False)
    scene = pyrender.Scene(bg_color=(0.95, 0.95, 0.93, 1.0), ambient_light=(0.35, 0.35, 0.35))
    add_meshes(scene, loaded)

    if args.view == "front":
        cam_pos = (0.0, -5.0, 1.0)
    elif args.view == "side":
        cam_pos = (5.0, -0.25, 1.0)
    else:
        cam_pos = (4.0, -5.0, 3.0)
    camera = pyrender.OrthographicCamera(xmag=2.3, ymag=2.3)
    scene.add(camera, pose=look_at(cam_pos))
    scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=3.0), pose=look_at((-3.0, -4.0, 6.0)))
    scene.add(pyrender.PointLight(color=np.ones(3), intensity=25.0), pose=np.array(
        [[1, 0, 0, 2.5], [0, 1, 0, -3.5], [0, 0, 1, 3.0], [0, 0, 0, 1]], dtype=np.float64
    ))

    renderer = pyrender.OffscreenRenderer(args.size, args.size)
    color, _ = renderer.render(scene, flags=pyrender.RenderFlags.RGBA)
    renderer.delete()
    imageio.imwrite(args.out, color)
    print(args.out)


if __name__ == "__main__":
    main()

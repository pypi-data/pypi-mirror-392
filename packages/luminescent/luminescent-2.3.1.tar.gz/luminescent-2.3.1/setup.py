from setuptools import setup, find_packages

setup(
    name="luminescent",  # Your package name
    version="2.3.1",  # Your package version
    description="GPU-accelerated fully differentiable FDTD for photonics and RF",
    author="Paul Shen",
    author_email="pxshen@alumni.stanford.edu",
    packages=find_packages(),  # Automatically find your package(s)
    install_requires=[
        "gdsfactory",
        "pymeshfix",
        "electromagneticpython",
        "sortedcontainers",
        "scikit-rf",
        "opencv-python",
        "femwell",
        "rasterio",
        "rtree",
        "gmsh",
        "manifold3d",
        "pymeshlab",
    ],
)
# cd luminescent
# python -m build
# twine upload dist/*

# pip install gdsfactory pillow pymeshfix electromagneticpython sortedcontainers scikit-rf
#

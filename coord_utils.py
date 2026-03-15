# coord_utils.py
# Converts in-game world coordinates (x, z) to minimap pixel positions.

IMAGE_SIZE = 1024  # all minimaps are 1024 x 1024 px

MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581,  "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}

MINIMAP_PATHS = {
    "AmbroseValley": "minimaps/AmbroseValley_Minimap.png",
    "GrandRift":     "minimaps/GrandRift_Minimap.png",
    "Lockdown":      "minimaps/Lockdown_Minimap.jpg",
}


def world_to_pixel(x: float, z: float, map_id: str) -> tuple[float, float]:
    """
    Convert world (x, z) to minimap pixel (px, py).

    Algorithm (from README):
        u = (x - origin_x) / scale          # 0..1 along horizontal axis
        v = (z - origin_z) / scale          # 0..1 along vertical axis
        px = u * IMAGE_SIZE
        py = (1 - v) * IMAGE_SIZE           # Y flipped: image origin is top-left

    NOTE: The 'y' column in the data is elevation and is NOT used for 2-D plotting.
    """
    cfg = MAP_CONFIG.get(map_id)
    if cfg is None:
        return 0.0, 0.0

    u = (x - cfg["origin_x"]) / cfg["scale"]
    v = (z - cfg["origin_z"]) / cfg["scale"]

    px = u * IMAGE_SIZE
    py = (1.0 - v) * IMAGE_SIZE  # flip Y

    return px, py

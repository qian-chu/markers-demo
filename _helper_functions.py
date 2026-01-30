import re
from time import time_ns

import cv2
import numpy as np
from psychopy import core, visual

APRILTAG_FAMILIES: list[str] = ["16h5", "25h9", "36h10", "36h11"]
ARUCO_SIZES: list[str] = ["4x4", "5x5", "6x6", "7x7"]
ARUCO_NUMBERS: list[str] = ["50", "100", "250", "1000"]


def marker_family_to_dict(marker_family: str) -> cv2.aruco.Dictionary:
    """
    Convert a marker family to a dictionary format with type identifier.

    Supports AprilTag and Aruco marker types. AprilTag markers use predefined
    size-denominator pairs (e.g., '36h10'), while Aruco markers use sizexnumber
    format (e.g., '6x6_250').
    """
    # AprilTags
    if marker_family in APRILTAG_FAMILIES:
        dict_name: str = f"DICT_APRILTAG_{marker_family.upper()}"
        aruco_dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dict_name))
        return "april", aruco_dict

    # ArUco Original
    if marker_family.lower() == "aruco_original":
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)
        return "aruco", aruco_dict

    # Other ArUco (format: {size}_{number})
    aruco_pattern = re.compile(r"^(\d+)x\1_(\d+)$")
    pattern_match = aruco_pattern.match(marker_family)

    if pattern_match:
        # Split marker name into size and number components
        size, number = marker_family.split("_")

        if size not in ARUCO_SIZES:
            raise ValueError(
                f"Invalid Aruco marker size '{size}' in '{marker_family}'. "
                f"Supported sizes: {', '.join(ARUCO_SIZES)}"
            )

        if number not in ARUCO_NUMBERS:
            raise ValueError(
                f"Invalid Aruco marker number '{number}' in '{marker_family}'. "
                f"Supported numbers: {', '.join(ARUCO_NUMBERS)}"
            )

        dict_name = f"DICT_{marker_family.upper()}"
        aruco_dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dict_name))
        return "aruco", aruco_dict

    # Provide helpful error message with supported formats
    raise ValueError(
        f"Unrecognized marker family '{marker_family}'. "
        f"Expected format:\n"
        f"  - AprilTag: {', '.join(APRILTAG_FAMILIES)}\n"
        f"  - Aruco: {{size}}_{{number}} (e.g., '6x6_250')\n"
        f"    Available sizes: {', '.join(ARUCO_SIZES)}\n"
        f"    Available numbers: {', '.join(ARUCO_NUMBERS)}"
    )


def generate_marker(
    marker_family: str,
    marker_id: int,
    marker_size_pixels: int,
):
    marker_type, aruco_dict = marker_family_to_dict(marker_family)
    img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size_pixels)
    # Convert to binary values {-1, 1}
    # OpenCV generates markers in {0, 255}; map 0 -> -1 and 255 -> 1
    img = np.where(img > 0, 1, -1).astype(np.int8)
    if marker_type == "april":
        # flip image diagonally for AprilTag markers
        # because AprilTag has a different orientation than ArUco
        # see https://github.com/opencv/opencv-python/issues/1195
        img = np.fliplr(img)
    else:
        # PsychoPy's y axis is flipped compared to OpenCV
        img = np.flipud(img)
    return img


def draw_markers(
    win, marker_family="36h11", n_markers=4, size=200, opacity=0.75, margin=50
):
    win_half_width, win_half_height = win.size / 2
    half_marker_size = size / 2

    x_positions = (
        -win_half_width + half_marker_size + margin,
        0,
        win_half_width - half_marker_size - margin,
    )
    y_positions = (
        win_half_height - half_marker_size - margin,
        0,
        -win_half_height + half_marker_size + margin,
    )
    # Clockwise order starting at top-left, excluding center
    order_indices = [
        (0, 0),  # top-left
        (1, 0),  # top-center
        (2, 0),  # top-right
        (2, 1),  # middle-right
        (2, 2),  # bottom-right
        (1, 2),  # bottom-center
        (0, 2),  # bottom-left
        (0, 1),  # middle-left
    ]
    all_positions = [(x_positions[i], y_positions[j]) for (i, j) in order_indices]
    if n_markers == 4:
        # corners: TL, TR, BR, BL
        positions_to_draw = [all_positions[i] for i in (0, 2, 4, 6)]
    elif n_markers == 6:
        # corners + side middles (ML, MR)
        positions_to_draw = [all_positions[i] for i in (0, 2, 3, 4, 6, 7)]
    else:
        positions_to_draw = all_positions

    marker_family = marker_family
    markers = [
        visual.ImageStim(
            win,
            image=generate_marker(
                marker_family=marker_family,
                marker_id=idx,
                marker_size_pixels=size,
            ),
            units="pix",
            size=size,
            pos=pos,
            opacity=opacity,
        )
        for idx, pos in enumerate(positions_to_draw)
    ]
    for marker in markers:
        marker.autoDraw = True


def send_event(device, event_name, clock_offset_ns):
    if device is not None:
        device.send_event(
            event_name,
            event_timestamp_unix_ns=int(time_ns() - clock_offset_ns),
        )


def end_exp(tracker, win):
    if tracker is not None:
        tracker.recording_stop_and_save()
        tracker.close()
    win.close()
    core.quit()

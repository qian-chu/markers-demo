import socket
import sys
from pathlib import Path
from random import shuffle

from psychopy import core, event, gui, visual
from pupil_labs.realtime_api.simple import Device

from _helper_functions import draw_markers, end_exp, send_event

DUMMY = True  # Set to False when running with Pupil Labs

# Generate default address using local machine's IP
full_address = socket.gethostbyname(socket.gethostname())
parts = full_address.split(".")
if len(parts) >= 4:
    address = ".".join(parts[:2]) + "."
else:
    address = full_address

tracker = None
offset_ns = 0
while not DUMMY:
    dlg = gui.Dlg()
    dlg.addField("Pupil Labs address", address)
    dlg.addField("Pupil Labs port", "8080")
    dlg_data = dlg.show()
    sys.exit() if not dlg.OK else None
    address, port = dlg_data.values()
    # Connect to Pupil Labs
    try:
        tracker = Device(address=address, port=port)
        offset_ns = round(
            tracker.estimate_time_offset().time_offset_ms.median * 1_000_000
        )
        break
    except Exception:
        dlg = gui.Dlg()
        dlg.addText("Failed to connect to Pupil Labs. Please try again.")
        dlg.show()

win = visual.Window(fullscr=True, units="pix")
win.mouseVisible = False
win.winHandle.activate()

# Prepare stimuli
text_stim = visual.TextStim(
    win,
    text="Press SPACE to begin the experiment",
    color="white",
)
fix_cross = visual.ShapeStim(
    win, vertices="cross", fillColor="white", lineColor=None, size=100, units="pix"
)
img = visual.ImageStim(win, size=(1200, 800), units="pix")
stimuli_dir = Path("stimuli")
img_paths = list(stimuli_dir.glob("*.jpg"))
shuffle(img_paths)

# Start experiment
draw_markers(win, "36h11", 6)
text_stim.draw()
win.flip()
event.waitKeys(keyList=["space"])
win.flip()

if not DUMMY:
    tracker.recording_start()
    core.wait(5)

# Present all images
for img_path in img_paths:
    img.image = str(img_path)
    fix_cross.draw()
    win.callOnFlip(send_event, tracker, "fixation", offset_ns)
    win.flip()
    core.wait(0.5)

    img.draw()
    win.callOnFlip(send_event, tracker, "image", offset_ns)
    win.flip()
    core.wait(4)

    win.flip()
    core.wait(1)

    keys = event.getKeys(["escape"])
    if "escape" in keys:
        end_exp(tracker, win)

end_exp(tracker, win)

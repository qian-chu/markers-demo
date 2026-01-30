from psychopy import event, visual

from _helper_functions import draw_markers, end_exp

tracker = None
win = visual.Window(fullscr=True, units="pix")
win.mouseVisible = False
win.winHandle.activate()

# Prepare stimuli
text_stim = visual.TextStim(
    win,
    text=(
        "This is a test run.\n"
        "Please take a picture of the screen and send to Qian.\n\n"
        "And on Neon companion device, go to the preview page (bottom right).\n"
        "Make sure the markers are clearly visible in the room's lighting condition.\n\n"
        "Press ESCAPE or space to end the test."
    ),
    color="red",
)
img = visual.Rect(
    win, size=(1200, 800), units="pix", lineColor="black", fillColor="white"
)

# Start experiment
draw_markers(win, "36h11", 6)
img.draw()
text_stim.draw()
win.flip()
event.waitKeys(keyList=["escape", "space"])
end_exp(tracker, win)

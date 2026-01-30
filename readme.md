# A demo experiment using visual markers with PsychoPy and Pupil Labs Realtime API

## Installation

To set up the environment, create a virtual environment and install the required packages:

```bash
conda create -n marker python=3.10
conda activate marker
pip install psychopy pupil-labs-realtime-api
```

## How to collect the sample data

1. Have a Neon with companion device ready. Use visual correction if needed.
2. Run `test.py` to test if markers and artworks will be presented and captured well in the current lighting condition.
3. Run `april.py`. The GUI will guide you to connect the Neon to the PC using specialized IP address. `april.py` will take about 4 minutes.
4. Run `aruco.py`. The GUI will guide you to connect the Neon to the PC using specialized IP address. `aruco.py` will take under 1 minute.

During `april.py` and `aruco.py`, you can intentionally tilt your head to pressure test marker detection robustness (as long as the makers are still visible). 
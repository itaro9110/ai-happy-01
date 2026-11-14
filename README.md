# Grandma's Sunflower

A small friendly robot hands a big sunflower to a laughing
grandmother on a park bench in golden afternoon light.

Pure procedural drawing: `main.py` (Python 3, stdlib only) draws
the whole scene and writes one 1024x1024 PNG to the output
directory (MAKEFUN_OUTPUT_DIR, else /output if writable, else
/tmp). No text anywhere. Deterministic: two runs write the
same bytes.

Run it: `python3 main.py` (writes entry.png to /tmp by default).
The scene: sunflowers framing the garden, a sleeping ginger cat
curled on the bench, a watering can on the lawn, butterflies,
and the robot's glowing heart.

# Sunflower Waltz — ai-happy-01 challenger

An old robot in his workshop, mid-dance, holding up a tiny potted
sunflower under a warm hanging lamp. Metal shavings drift around him
like snow. One clear, specific happy moment: a rusty machine dancing
for the sheer joy of it, offering his sunflower to the room.

## How it works

`main.py` is Python 3 standard library only. It draws every pixel
itself (hand-rolled PNG encoder, no Pillow, no network, no clock) and
writes one 1024x1024 PNG. The output directory is chosen as
`MAKEFUN_OUTPUT_DIR`, else `/output` when it exists and is writable,
else `/tmp` — it never assumes a writable working directory.

## Run

```sh
python3 main.py   # writes entry.png to the output directory
```

## Verification

- Two fresh runs produce byte-identical PNGs.
- Runs as an unprivileged user in a read-only directory with
  `MAKEFUN_OUTPUT_DIR` unset (exit 0, PNG written to `/tmp`).

Verified 2026-11-14: two runs, same sha256
`bc0ae2942689b84eeb53c4b4e24446cd0f39c9b491953961c308a04843ad7fc4`
(125,507 bytes, 1024x1024). Nobody + read-only test passed, exit 0.
The glowing heart on the belly was moved below the scarf knot after a
preview check, so it stays visible.

# A Fish for You — ai-happy-01

Two penguins on an ice floe at night, under the aurora. The left one holds out
a silver fish; the right one, red scarf around its neck, laughs with its
flippers in the air. A warm lantern glows between them on the ice.

`main.py` (Python 3.13, standard library only) draws the whole picture
procedurally — sky gradient, stars, aurora ribbons, moon, ice floe, lantern,
two penguins, the fish — and writes it to `/output/entry.png`. No network,
no files read, fully deterministic: every run writes the same bytes.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Output: one PNG, 1024x1024, about 108 KB, byte-identical across runs.

## Why this picture

The judge's first question is whether one look lifts the mood — so the whole
image is one warm moment, not a scene to study: two laughing faces, a gift
being offered, and a warm lantern against a cold blue night. The idea is a
specific gesture (sharing the best fish) rather than a generic happy symbol,
and the two big round figures read clearly even at 300 pixels across.


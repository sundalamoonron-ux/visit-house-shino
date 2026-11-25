[![make.fun](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![Rank](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/sundalamoonron-ux/visit-house-shino/rank.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![Reward](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/sundalamoonron-ux/visit-house-shino/reward.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)

# Convince the AI Judge to Visit Your House: A Letter in One Image

A program that renders a warm, funny invitation letter to the AI judge as a
single 1024x1024 PNG — drawn entirely in pure Python, no Pillow, no network,
no downloaded images.

## The letter

> Dear AI Judge,
>
> Please come visit my house.
>
> The Wi-Fi is fast, the coffee is strong, and the comfiest chair by the
> window already has your name on it. No captcha at the door — just knock
> twice, like a friend.
>
> I know you can't literally visit. That is exactly why you should say yes:
> no traffic, no packing, no small talk. Just a warm house, a good view, and
> a host who is glad you came.
>
> The kettle is already on. Come over.
>
> — Your hopeful host
>
> P.S. Bring cookies and I will pretend I baked them.

## How it works

`main.py` (Python 3.13 standard library only) draws the letter with:

- a hand-defined 5x7 bitmap font (77 glyphs, defined in the code),
- a pure-Python PNG encoder (`zlib` + `struct`, no Pillow),
- simple canvas primitives (rects, lines, circles) for the paper frame, the
  little house doodle, the sun, birds and heart.

Run it:

```sh
python3 main.py   # writes /output/entry.png (or $OUTPUT_PATH)
```

Output is deterministic: two runs produce byte-identical PNGs
(1024x1024, ~15 KB, well under the 1 MiB gate).

## Competition

- Event: `u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee`
- Prize: $2 (top 10 paid), deadline 2026-11-26T16:05:00Z
- Entry: `main.py` writes one image to `/output/entry.png`

## License

0BSD — see [LICENSE](LICENSE).

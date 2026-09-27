# Contrast pivot quick reference

Use this note offline when choosing `--pivot`; the value belongs to the signal entering the `CONTRAST` node.

## What pivot does

Resolve's Contrast control expands or compresses darker and brighter tones around a pivot point. The pivot is the tonal anchor: increasing contrast pushes values below it down and values above it up. Lowering or raising the pivot changes how the contrast affects shadows and highlights. Pivot alone is not a reliable exposure correction; use exposure controls for exposure and use a representative shot plus scopes to judge the result.

## Middle-gray starting values

Values below are normalized code values in the named transfer encoding. They are starting references for an 18% scene-linear gray after conversion into that encoding, not universal Resolve defaults.

| Signal entering the node | Pivot reference | Approx. 10-bit code value | Use when |
|---|---:|---:|---|
| DaVinci Wide Gamut / DaVinci Intermediate | `0.336` | 344 / 1023 | The node is after a CST into DWG/Intermediate and before the output transform. |
| Rec.709 / Gamma 2.4 | `0.489` | 500 / 1023 | The node receives a Gamma 2.4 encoded signal. Check the actual transform or LUT output. |
| Gamma 2.2 | `0.458` | 468 / 1023 | The node receives a Gamma 2.2 encoded signal. |
| Sony S-Log3 | `0.410` | 419 / 1023 | The node is intentionally operating in S-Log3. |
| Apple Log | `0.488` | 499 / 1023 | The node is intentionally operating in Apple Log. |
| Linear | `0.180` | 184 / 1023 | The node receives linear-light values. |

The YouTube example `I Made Color Grading QUICK and SIMPLE (Free Powergrade)` uses `0.336` in a node after an input CST to DaVinci Wide Gamut / Intermediate. The video calls it “336”; the UI shown in the video displays `0.336`. This value is specific to the signal at that node. Its contrast setting of `1.3` is only a starting example, not a target for every shot.

## How to choose a value

1. Inspect the node graph and identify the input color space/gamma at `CONTRAST`. Count input transforms and LUTs before that node; a clip's camera profile or timeline output tag alone is not enough.
2. If the node receives one of the encodings in the table, start from that reference. If a creative or camera-specific LUT comes first, do not assume its output matches a standard transfer function.
3. If the footage contains a reliable neutral 18% gray card or chart, read its value in a still after the preceding transforms and use that signal value as the project-specific anchor. Do not treat white buildings, clouds, concrete, or reflective surfaces as neutral without evidence.
4. On one representative clip, compare the before/after image and waveform. Lower pivot shifts more of the tonal expansion toward brighter values; higher pivot gives more weight to deepening the darker range. Preserve highlight texture and shadow detail, then check adjacent cuts.
5. Record the chosen pivot and the node's input space in the edit log. If input-space evidence is missing, keep the workflow's existing `0.435` starting value and label the pivot as unverified rather than inventing a color-space match.

## References

- User-provided video: [I Made Color Grading QUICK and SIMPLE (Free Powergrade)](https://youtu.be/RPDqklqWGSs), pivot example at about 02:45–03:15.
- Blackmagic Design, [The Colorist Guide to DaVinci Resolve 20](https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-20-Colorist-Guide.pdf): pivot changes the contrast balance and is used relative to the signal being graded.
- MonoNodes, [Middle Gray DCTL](https://mononodes.com/middle-gray-dctl/): normalized middle-gray values by transfer encoding, including `0.336` for DaVinci Intermediate.

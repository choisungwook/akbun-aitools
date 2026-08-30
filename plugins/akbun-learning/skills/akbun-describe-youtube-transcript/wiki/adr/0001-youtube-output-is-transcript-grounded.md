# YouTube Output Is Transcript Grounded

## Decision

Produce a chronological Markdown transcript rather than a short summary or commentary. Use cleaned captions as the primary input and raw VTT only as fallback evidence.

## Reason

Automatic captions contain rolling duplication and karaoke tags. Cleaning those artifacts preserves the spoken record without adding content that was not in the video.


Currently known as VentoGiusto, formally known as DiamondIsFixed. Neither cleaned up nor presentable.

Requirements:

* Python (should work with 2 or 3)
* youtube-dl libraries
* mkvtoolnix

## crget

Have a file called **cookies.txt** in the same directory as `crget.py` containing the exported cookies from a logged in Crunchyroll account. You may need to add the user agent the cookies were exported from in line 32. Then run the script with the URL as parameter.

```
python crget.py <URL>
```

This should output one video file (mp4) and one English subtitle file (enUS.ass).

## crazydiamond

```
python crazydiamond.py "some_video_url." [-m]
```

Pass the episode file name up to *and including* the first full stop as parameter. The `-m` option will halt the program just before muxing, so you can do extra manual edits to the sub file if you wish. Hit enter to continue if in manual mode.

Make sure the `OpenSans-Semibold.ttf` is in the same directory as the script.

`CR_NAMES` on line 7 is the list of replacements. Add to it if you need more.

Right under is `OP_TIME` and `ED_TIME`. Change these to match the lengths of the current OP/EDs for the auto-chaptering. Format: **HH:MM:SS.mm**.





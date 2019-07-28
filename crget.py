import sys
import youtube_dl 

header = '[Script Info]\n' \
        'Title: VentoGiusto\n' \
        'ScriptType: v4.00+\n' \
        'WrapStyle: 0\n' \
        'PlayResX: 848\n' \
        'PlayResY: 480\n' \
        'ScaledBorderAndShadow: yes\n'

# First it will find a no-sub 720p video to download
ydl = youtube_dl.YoutubeDL({'cookiefile': 'cookies.txt'})

with ydl:
    result = ydl.extract_info(sys.argv[1].strip(), download=False)

# JoJo's Bizarre Adventure - Golden Wind Episode %d [emdash] [Episode Name]-[display_id]
base_name = result["title"].replace(":", " -").replace(u"\u2013", "-") + "-" + result["display_id"]

valid_formats = []
for cr_format in result["formats"]:
    if cr_format["height"] == 720 and "hardsub" not in cr_format["format"]:
        valid_formats.append(cr_format)

# Here it will grab the video and subtitle file separately
opts = {'cookiefile': 'cookies.txt',
        'writesubtitles': True,
        'subtitleslangs': ['enUS'],
        'format': valid_formats[0]["format_id"],
        'outtmpl': base_name + '.%(ext)s',
        'user-agent': '"Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"',
        #'user-agent': '"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"',
        'skip_download': False 
        }
ydl = youtube_dl.YoutubeDL(opts)
with ydl:
    ydl.download([sys.argv[1].strip()])

print("\nReplacing subtitle header.")

with open(base_name + ".enUS.ass", "r") as f:
    sublines = f.read().split('\n')

for i in range(len(sublines)):
    if sublines[i].strip() == "[V4+ Styles]":
        break

if i < len(sublines) - 1:
    with open(base_name + ".enUS.ass", "w") as f:
        f.write("%s\n%s" % (header, '\n'.join(sublines[i:])))

print("Files written to \"%s\"" % base_name)

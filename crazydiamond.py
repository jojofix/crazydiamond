import os
import sys
import math
import signal
from datetime import datetime

CR_NAMES = {
    'Shining Diamond': 'Crazy Diamond',
    'Reverb': 'Echoes',
    'Show Off': 'Surface',
    'Worse Company': 'Bad Company',
    'Chili Pepper': 'Red Hot Chili Pepper',
    'Trendy': 'Trussardi',
    'Pole Jam': 'Pearl Jam',
    'Deadly Queen': 'Killer Queen',
    'Heart Attack': 'Sheer Heart Attack',
    'Heart Father': 'Atom Heart Father',
    'Terra Ventus': 'Earth Wind & Fire',
    'Highway Go Go': 'Highway Star',
    'Misterioso': 'Enigma',
    'Cheap Trap': 'Cheap Trick',
    'Golden Wind': 'Gold Experience',
    'Zipper Man': 'Sticky Fingers',
    'Shadow Sabbath': 'Black Sabbath',
    'Moody Jazz': 'Moody Blues',
    'Tender Machine': 'Soft Machine',
    'Six Bullets': 'Sex Pistols',
    'Arts & Crafts': 'Kraft Work',
    "Li\'l Bomber": 'Aerosmith',
    'Tiny Feet': 'Little Feet',
    'Mirror Man': 'Man in the Mirror',
    'Purple Smoke': 'Purple Haze',
    'Coco Large': 'Coco Jumbo',
    'Fisher Man': 'Beach Boy',
    'Thankful Death': 'Grateful Dead',
    'Babyhead': 'Baby Face',
    'White Ice': 'White Album',
    'Emperor Crimson': 'King Crimson',
    'Crush': 'Clash',
    'Talking Mouth': 'Talking Head',
    'Notorious Chase': 'Notorious B.I.G.',
    'Spicy Lady': 'Spice Girl',
    'Metallic': 'Metallica',
    'Eulogy': 'Epitaph',
    'Green Tea': 'Green Day',
    'Sanctuary': 'Oasis'
}

# Needs to be changed for every OP/ED
OP_TIME = "00:01:53.00"
ED_TIME = "00:01:40.00"

# All this shit is mostly just for the eyecatch
class Subtitle:
    raw = None
    sformat = None
    layer  = None
    start  = None
    end    = None
    style  = None
    name   = None
    marginL = None
    marginY = None
    marginV = None
    effect  = None
    text    = ''
    
    modified = False
    
    def __init__(self, line, linenum):
        self.linenum = linenum
        line = line.strip()

        if len(line) < 1:
            self.sformat = "null"
            return

        p = line.partition(' ')
        self.sformat = p[0].strip().replace(':','')

        rest = p[2].split(',')
        
        if self.sformat == "Style":
            [self.name, self.fontname, self.fontsize] = rest[0:3]
            [self.color1, self.color2, self.ocolor, self.bcolor] = rest[3:7]
            [self.bold, self.italic, self.underline, self.strike] = rest[7:11]
            [self.scaleX, self.scaleY, self.spacing, self.angle] = rest[11:15]
            [self.bstyle, self.outline, self.shadow] = rest[15:18]
            [self.alignment, self.marginL, self.marginR, self.marginV] = rest[18:22]
            self.encoding = rest[22]
        elif self.sformat == "Dialogue":
            self.layer  = rest[0]
            self.start  = rest[1]
            self.end    = rest[2]
            self.style  = rest[3]
            self.name   = rest[4]
            self.marginL = rest[5]
            self.marginY = rest[6]
            self.marginV = rest[7]
            self.effect = rest[8]
            self.text   = ','.join(rest[9:]).strip()
        else:
            self.sformat = "null"

    def reconstruct(self):
        if self.sformat == "Dialogue":
            subinfo = ','.join([self.layer, self.start, self.end, self.style,
                                self.name, self.marginL, self.marginY,
                                self.marginV, self.effect, self.text])
            fixedline = self.sformat + ': ' + subinfo
        elif self.sformat == "Style":
            subinfo = ','.join([self.name, self.fontname, self.fontsize,
                                self.color1, self.color2, self.ocolor,
                                self.bcolor, self.bold, self.italic,
                                self.underline, self.strike, self.scaleX,
                                self.scaleY, self.spacing, self.angle,
                                self.bstyle, self.outline, self.shadow,
                                self.alignment, self.marginL, self.marginR,
                                self.marginV, self.encoding])
            fixedline = self.sformat + ': ' + subinfo
        else:
            fixedline = ''
        return fixedline

def signal_exit(sig, frame):
    print("\nCanceling sub fix.")
    sys.exit(0)

def time_delta_to_string(tdelta):
    s = tdelta.total_seconds()

    opstamp = "%02d:%02d:%02d.00" % (s // 3600, s % 3600 // 60, s % 60)
    return opstamp
    
def calculate_OP_time(ep_timestamp):
    d_ep = datetime.strptime(ep_timestamp, "%H:%M:%S.%f")
    d_op_len = datetime.strptime(OP_TIME, "%H:%M:%S.%f")

    tdelta = d_ep - d_op_len
    return time_delta_to_string(tdelta)

def check_OPED_exists(subs, i, S_TIME):
    # This is likely needlessly complicated and I'm just retarded.
    # That probably sums up this entire script.
    d_next = datetime.strptime(subs[i].start, "%H:%M:%S.%f")
    if subs[i-1].end is not None:
        d_prev = datetime.strptime(subs[i-1].end, "%H:%M:%S.%f")
    else:
        return False
    d_prev = datetime.strptime(subs[i-1].end, "%H:%M:%S.%f")
    d_ed_len = datetime.strptime(ED_TIME, "%H:%M:%S.%f")
    d_ed = datetime.strptime(time_delta_to_string(d_next - d_ed_len), "%H:%M:%S.%f")

    return d_prev < d_ed

def calculate_ED_time(ep_timestamp):
    d_next = datetime.strptime(ep_timestamp, "%H:%M:%S.%f")
    d_ed_len = datetime.strptime(ED_TIME, "%H:%M:%S.%f")

    tdelta = d_next - d_ed_len
    return time_delta_to_string(tdelta)

def adjust_eyecatch_margin(oldtext, newtext, catchstyle, styles, resx):
    stylesub = styles[catchstyle]
    marginL = int(stylesub.marginL)

    if marginL > int(resx) / 2:
        diff = float(len(newtext)) / len(oldtext)
        if diff > 1:
            adjust = math.floor(diff * 70)
            new_margin = marginL - adjust

            stylesub.marginL = "%d" % new_margin
            stylesub.modified = True

# Legacy from Part 4
def filter_eyecatch(subs, i, styles, resx):
    catchstyle = subs[i].style
    oldtext = subs[i].text

    j = i

    while subs[i - 1].style == catchstyle:
        i = i - 1

    i_next = j + 1

    if any([name in subs[j].text for name in CR_NAMES]):
        base_length = len(subs[j].text.strip())

        new_name = subs[j].text
        for name in CR_NAMES:
            new_name = new_name.replace(name, CR_NAMES[name])
            
        print("EYECATCH FIX: " + subs[j].start + " " + new_name)
        # Take the percentage of text removed during the eyecatch scroll
        # Apply that to the new text to recreate it in the replaced name
        while j >= i:
            catch_text = subs[j].text.strip()
            replace_len = int(math.ceil(len(new_name) * len(catch_text) / float(base_length)))
            subs[j].text = new_name[0:replace_len]
            subs[j].modified = True
            j = j - 1

        adjust_eyecatch_margin(oldtext, new_name, catchstyle, styles, resx)

    return i_next

# If this function is needed it will probably not work due to color formats
# Print statements are there to know what to fix manually
def filter_next_title(subs, i):
    i_next = i + 1
    if i + 1 >= len(subs) or subs[i].modified:
        return i_next
    
    for name in CR_NAMES:
        if name in subs[i].text:
            subs[i].text = subs[i].text.replace(name, CR_NAMES[name])
            subs[i].modified = True
            print("NEXTTITLE FIX: " + subs[i].text)
        if name in subs[i + 1].text:
            subs[i + 1].text = subs[i + 1].text.replace(name, CR_NAMES[name])
            subs[i + 1].modified = True
            print("NEXTTITLE FIX" + subs[i].text)

    return i_next

# Usage: crazydiamond.py VIDEO_FILE [ -m ]
# -m halts for manual sub edits if needed
def main(args):
    signal.signal(signal.SIGINT, signal_exit)

    videosrc = args[1].strip() + "mp4"
    subsrc   = args[1].strip() + "enUS.ass"
    ep_no = videosrc.split("Episode")[1].split()[0].zfill(2)

    manual_mode = "-m" in args
    
    base_name = "[VentoGiusto] JoJo's Bizarre Adventure - Golden Wind " + ep_no

    new_video = base_name + ".mkv"
    subfile = base_name + ".ass"
    chapterfile = subfile.replace(".ass", ".chapters")

    print("\nCrazy Diamond is fixing the subtitles...\n")

    with open(subsrc, 'r') as f:
        lines = f.read().split('\n')

    subs = []
    for linenum in range(0, len(lines)):
        subs.append(Subtitle(lines[linenum], linenum))

    CR_word_check = []
    for word in CR_NAMES:
        CR_word_check += word.split()
    CR_word_check = list(set(CR_word_check))

    CR_keys = []
    for name in CR_NAMES:
        CR_keys += CR_NAMES[name].split()
    CR_keys = list(set(CR_keys))

    CR_word_check = list(set(CR_word_check) - set(CR_keys))

    chapter_list = ['00:00:00.00']

    OP_present = False
    next_title_found = False
    styles = {}
    resx = 0

    i = 0
    while subs[i].sformat != "Dialogue":
        if subs[i].sformat == "null":
            if lines[i].startswith("PlayResX"):
                resx = int(lines[i].split()[1])
        elif subs[i].sformat == "Style":
            subs[i].fontname = "Open Sans Semibold"
            size = round(1.5 * int(subs[i].fontsize))
            if size < 36: size = 36
            subs[i].fontsize = str(int(size))

            mv = round(1.33 * float(subs[i].marginV))
            if mv < 28: mv = 28
            subs[i].marginV = str(int(mv))
            subs[i].modified = True

            styles[subs[i].name] = subs[i]
            
        i = i + 1
        
    while i < len(subs):
        if subs[i].sformat in ("null", "Style"):
            i = i + 1
            continue

        if subs[i].style.startswith("JoJo-MainTitle"):
            OP_present = True
            continue

        if subs[i].style.startswith("JoJo-EpTitle"):
            if OP_present:
                opstamp = calculate_OP_time(subs[i].start)
                chapter_list.append(opstamp)
                
            if check_OPED_exists(subs, i, OP_TIME):
                opstamp = calculate_OP_time(subs[i].start)
                chapter_list.append(opstamp)
            chapter_list.append(subs[i].start)

        if (subs[i-2].text == subs[i-1].text[0:len(subs[i-2].text)] == subs[i].text[0:len(subs[i-2].text)]
            and subs[i+1].style != subs[i].style
            and len(subs[i-2].text) > 1):
            print("CATCH: " + subs[i].start + ' ' + subs[i].text)
            i = filter_eyecatch(subs, i, styles, resx)
            if subs[i - 1].end not in chapter_list:
                chapter_list.append(subs[i - 1].end)
            else:
                i += 1
        elif subs[i].style.startswith("JoJo-Eyecatch"):
            print("CATCH: " + subs[i].start + ' ' + subs[i].text)
            oldtext = subs[i].text.split("}")[-1]
            catchstyle = subs[i].style

            for name in CR_NAMES:
                if name in subs[i].text:
                    subs[i].text = subs[i].text.replace(name, CR_NAMES[name])
                    subs[i].modified = True

            if subs[i].modified:
                print("EYECATCH FIX: " + subs[i].start + ' ' + subs[i].text)
                adjust_eyecatch_margin(oldtext, subs[i].text.split("}")[-1], catchstyle, styles, resx)

            if subs[i].end not in chapter_list:
                chapter_list.append(subs[i].end)

            i += 1
        elif subs[i].style.startswith("JoJo-NextTitle"):
            if not next_title_found:
                print("NEXT: " + subs[i].text)
                next_title_found = True
                if check_OPED_exists(subs, i, ED_TIME):
                    edstamp = calculate_ED_time(subs[i].start)
                    chapter_list.append(edstamp)
                chapter_list.append(subs[i].start)
            i = filter_next_title(subs, i)
        else:
            for name in CR_NAMES:
                if name in subs[i].text:
                    subs[i].text = subs[i].text.replace(name, CR_NAMES[name])
                    subs[i].modified = True
                    print(subs[i].start + ' ' + subs[i].text)
            for word in CR_word_check:
                if word in subs[i].text:
                    print("WARN: [" + word + "] " + subs[i].start + ' ' + subs[i].text) 
            i = i + 1

    with open(subfile, 'w') as f:
        for i in range(0, len(subs)):
            if subs[i].modified:
                f.write(subs[i].reconstruct() + '\n')
            else:
                f.write(lines[i] + '\n')

    print("\nAssembling chapters...\n")
    print('\n'.join(chapter_list) + '\n')

    # Uses simple chapter format
    with open(chapterfile, 'w') as f:
        chap_no = 1

        for chapter in chapter_list:
            f.write("CHAPTER%02d=%s\n" % (chap_no, chapter))
            f.write("CHAPTER%02dNAME=%02d\n" % (chap_no, chap_no))
            chap_no += 1

    if manual_mode:
        # Fuck this
        if sys.version_info >= (3, 0):
            input("Halting program for manual edits.\n")
        else:
            raw_input("Halting program for manual edits.\n")
        print("Resuming mux.")
            
    attach = "--attachment-mime-type application/x-truetype-font "
    attach += "--attach-file OpenSans-Semibold.ttf"
    os.system("mkvmerge -o \"%s\" -S \"%s\" --language \"0:eng\" \"%s\" --chapters \"%s\" %s"
              % (new_video, videosrc, subfile, chapterfile, attach))

    os.remove(chapterfile)
                
if __name__ == "__main__":
    main(sys.argv)

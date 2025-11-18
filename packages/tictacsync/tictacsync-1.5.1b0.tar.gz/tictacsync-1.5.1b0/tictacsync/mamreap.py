import json, pathlib, itertools, os, re, ffmpeg, shutil, time, random
import argparse, platformdirs, configparser, sys, collections
from loguru import logger
from pprint import pformat
from dataclasses import dataclass
from rich import print
from enum import Enum
from rich.progress import Progress
from matplotlib.colors import hsv_to_rgb

try:
    from . import mamconf
    from . import mamdav
except:
    import mamconf
    import mamdav

dev = 'Cockos Incorporated'
app ='REAPER'
MAC = pathlib.Path(platformdirs.user_data_dir(app, dev)) / 'Scripts' / 'Atomic'
WIN = pathlib.Path(platformdirs.user_data_dir('Scripts', 'Reaper', roaming=True))

is_windows = hasattr(sys, 'getwindowsversion')
REAPER_SCRIPT_LOCATION = WIN if is_windows else MAC

REAPER_LUA_CODE = """reaper.Main_OnCommand(40577, 0) -- lock left/right move
reaper.Main_OnCommand(40569, 0) -- lock enabled
reaper.Main_OnCommand(50125, 0) -- show video window

local function placeWavsBeginingAtTrack(clip, start_idx, name)
  for i, file in ipairs(clip.files) do
    local item_col = clip.colors[i]
    local track_idx = start_idx + i - 1
    local track = reaper.GetTrack(nil,track_idx-1)
    reaper.GetSetMediaTrackInfo_String(track, "P_NAME",name, true)
    reaper.SetOnlyTrackSelected(track)
    local left_trim = clip.in_time - clip.start_time
    local where = clip.timeline_pos - left_trim
    reaper.SetEditCurPos(where, false, false)
    reaper.InsertMedia(file, 0 )
    local item_cnt = reaper.CountTrackMediaItems( track )
    local item = reaper.GetTrackMediaItem( track, item_cnt-1 )
    reaper.SetMediaItemInfo_Value(item, "I_CUSTOMCOLOR", item_col | 0x1000000)
    -- local take = reaper.GetTake(item, 0)
    -- reaper.GetSetMediaItemTakeInfo_String(take, "P_NAME", clip.name, true)
    local pos = reaper.GetMediaItemInfo_Value(item, "D_POSITION")
    reaper.BR_SetItemEdges(item, clip.timeline_pos, clip.timeline_pos + clip.cut_duration)
    reaper.SetMediaItemInfo_Value(item, "C_LOCK", 2)
  end
end

--cut here--

sample of the clips nested table (this will be discarded)
each clip has an EDL info table plus a sequence of ISO files:

clips =
{
{
    name="canon24fps01.MOV", start_time=7.25, in_time=21.125, cut_duration=6.875, timeline_pos=3600,
    files=
        {
        "/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/leftCAM/card01/canon24fps01_SND/ISOfiles/Alice_canon24fps01.wav",
        "/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/leftCAM/card01/canon24fps01_SND/ISOfiles/Bob_canon24fps01.wav"
        }
},
{name="DSC_8063.MOV", start_time=0.0, in_time=5.0, cut_duration=20.25, timeline_pos=3606.875,
files={"/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/rightCAM/ROLL01/DSC_8063_SND/ISOfiles/Alice_DSC_8063.wav",
"/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/rightCAM/ROLL01/DSC_8063_SND/ISOfiles/Bob_DSC_8063.wav"}},
{name="canon24fps02.MOV", start_time=35.166666666666664, in_time=35.166666666666664, cut_duration=20.541666666666668, timeline_pos=3627.125, files={"/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/leftCAM/card01/canon24fps02_SND/ISOfiles/Alice_canon24fps02.wav",
"/Users/lutzray/Downloads/SoundForMyMovie/MyBigMovie/day01/leftCAM/card01/canon24fps02_SND/ISOfiles/Bob_canon24fps02.wav"}}
}

--cut here--
-- make room fro the tracks to come
amplitude_top = 0
amplitude_bottom = 0
for i_clip, cl in pairs(clips) do
  if i_clip%2 ~= 1 then
    amplitude_top = math.max(amplitude_top, #cl.files)
  else
    amplitude_bottom = math.max(amplitude_bottom, #cl.files)
  end
end
for i = 1 , amplitude_top + amplitude_bottom + 1 do
  reaper.InsertTrackAtIndex( -1, false ) -- at end
end
track_count = reaper.CountTracks(0)
-- ISOs will be up and down the base_track index
base_track = track_count - amplitude_bottom
for iclip, clip in ipairs(clips) do
  -- go, place files on track
  start_track_number = base_track
  -- alternating even/odd, odd=below base_track 
  if iclip%2 == 0 then -- above base_track, start higher
    start_track_number = base_track - #clip.files
  end
  placeWavsBeginingAtTrack(clip, start_track_number, timeline_name)
  -- if #clips > 1 then -- interclips editing
  reaper.AddProjectMarker(0, false, clip.timeline_pos, 0, '', -1)
  -- end
end
reaper.SetEditCurPos(3600, false, false)
reaper.Main_OnCommand(40151, 0)
-- if #clips > 1 then -- interclips editing
-- last marker at the end
last_clip = clips[#clips]
reaper.AddProjectMarker(0, false, last_clip.timeline_pos + last_clip.cut_duration, 0, '', -1)
-- end

"""
v_file_extensions = \
"""MOV webm mkv flv flv vob ogv ogg drc gif gifv mng avi MTS M2TS TS mov qt
wmv yuv rm rmvb viv asf amv mp4 m4p m4v mpg mp2 mpeg mpe mpv mpg mpeg m2v
m4v svi 3gp 3g2 mxf roq nsv flv f4v f4p f4a f4b 3gp""".split()

logger.remove()
logger.level("DEBUG", color="<yellow>")
# logger.add(sys.stdout, level="DEBUG")


import hashlib

def string_to_float(text): # Deepseek :-)
    """
    Convert a string to a reproducible random float between 0 and 1.
    
    Args:
        text (str): Input string
        
    Returns:
        float: Random float between 0 and 1
    """
    # Create MD5 hash of the string
    hash_object = hashlib.md5(text.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    
    # Convert first 8 characters of hash to integer and normalize to 0-1
    hash_int = int(hash_hex[:8], 16)
    return hash_int / 0xFFFFFFFF

# logger.add(sys.stdout, filter=lambda r: r["function"] == "rnd_col")
def rnd_col(string, hue_rnd):
    # hue_rnd is in [0; 1[ 
    # returns random hued Reaper color
    h = (string_to_float(string) + hue_rnd)%1
    logger.debug(f'for {string} h:{h} ')
    # s, v = (255/255, 255/255)
    s, v = (0.5, 0.9)
    rr, gg, bb = [f'{int(v*255):0x}'.upper().zfill(2) for v in hsv_to_rgb((h, s, v))]
    logger.debug(f'rr: {rr} gg: {gg}, bb:{bb}')
    retval = '0x' + bb + gg + rr
    # print(retval)
    return retval

def rounded_int(x):
    return int(round(x))

# class Modes(Enum):
#     INTRACLIP = 1 # send-to-sound --clip DSC085 -> find the ISOs, load the clip in Reaper
#     INTERCLIP_SOME = 2 # send-to-sound cut27.otio cut27.mov
#             # cut27.mov has TC + duration -> can find clips in otio...
#             # place cut27.mov according to its TC
#             # Reaper will then produces a cut27mix.wav saved in SNDROOT/postprod
#     INTERCLIP_ALL = 3 # send-to-sound cut27.otio -> whole project

# logger.add(sys.stdout, filter=lambda r: r["function"] == "parse_otio_args")
def parse_otio_args():
    """
    Check for inconsistencies in user input. Complete program mode of action
    will be determined later with otio and *mov length.

    Returns otio_file, movie_file, clip_names, exit_flag.

    clip_names is a tuple of clip names (maybe abbreviated);
    tuple length is one if -c option is used, two otherwise, or zero.

    movie_file is None if not given as arg.

    exit_flag is True if -e option is parsed

    Examples of invocations:

        mamreap cut28.otio cut28.mov -> INTERCLIP_ALL if same lengths
        mamreap cut28.otio -> INTERCLIP_ALL
        mamreap -c 8064 -> INTRACLIP
        mamreap cut28.otio cut28.mov -> INTERCLIP_SOME if lengths differ
        mamreap cut28.otio cut28.mov 8064 ps01 -> INTERCLIP_SOME
        mamreap cut28.otio 8064 ps01  -> INTERCLIP_SOME
    """

    descr = """Take the video clip (-c option) or parse the submitted OTIO timeline
    to build a Reaper Script which loads the corresponding
    ISO files from SNDROOT (see mamconf --show)."""
    parser = argparse.ArgumentParser(description=descr,
        epilog="""NB: -c option uses a FILENAME abbreviation; in other cases you
        must use clip names set in Davinci Resolve.""")
    parser.add_argument('-e',
                    action='store_true',
                    help="exit on completion (don't wait for the wav mix to be rendered by Reaper)")
    parser.add_argument('-t',
                    action='store_true',
                    help="Include timecode track")
    parser.add_argument('-c',
                    dest='clip_arg',
                    nargs=1,
                    help="send only this specified clip to Reaper (partial filename is OK)")
    parser.add_argument('otio_and_al', nargs='*', help='an otio file and a pair of clip names, or a .mov')
    args = parser.parse_args()
    logger.debug('args %s'%args)
    if args.clip_arg != None:
        if args.otio_and_al != []:
            print('Error: -c "<A_CLIP>" option should be used alone without any other argument. Bye.')
            sys.exit(0)
        else:
            # e.g. mamreap -c DSC087
            clip_names = args.clip_arg[0]
            logger.debug('mode, c_option_arg, otio_file, render_file, exit:')
            return None, None, clip_names, args.e #############################
    def _is_otio(f):
        components = f.split('.')
        if len(components) == 1:
            return False
        return components[-1].lower() == 'otio'
    def _is_video(f):
        components = f.split('.')
        if len(components) == 1:
            return False
        return components[-1].lower() in v_file_extensions
    # otio = ?
    otio_candidate = [a for a in args.otio_and_al if _is_otio(a)]
    if len(otio_candidate) > 1:
        print(f'Error: one OTIO file is needed, not {len(otio_candidate)}. Bye.')
        sys.exit(0)
    if len(otio_candidate) == 0:
        print('Error: an OTIO file (or a -c argument) is needed. Bye.')
        sys.exit(0)
    else:
        otio_file = otio_candidate[0]
    # MOV?
    mov_candidate = [a for a in args.otio_and_al if _is_video(a)]
    if len(mov_candidate) > 1:
        print(f'Error: one video file at most is needed, not {len(mov_candidate)}. Bye.')
        sys.exit(0)
    if len(mov_candidate) == 1:
        movie_file = mov_candidate[0]
    else:
        movie_file = None
    # clips?
    clips = [a for a in args.otio_and_al if not _is_video(a) and not _is_otio(a)]
    if len(clips) > 2:
        print(f'Error: too many clips (2 max), bye.')
        sys.exit(0)
    clip_names = clips
    return otio_file, movie_file, clip_names, args.e, args.t #########################

@dataclass
class Clip:
    # all time in seconds
    start_time: float # the start time of the clip, != 0 if metadata TC
    in_time: float # time of 'in' point, if in_time == start_time, no left trim
    cut_duration: float # with this value, right trim is detemined, if needed
    whole_duration: float # unedited clip duration
    name: str #
    path: str # path of clip
    timeline_pos: float # when on the timeline the clip starts
    ISOdir: None # folder of ISO files for clip

def clip_info_from_json(jsoncl):
    """
    parse data from an OTIO json Clip
    https://opentimelineio.readthedocs.io/en/latest/tutorials/otio-serialized-schema.html#clip-2
    returns a list composed of (all times are in seconds):
        st, start time (from clip metadata TC) 
        In, the "in time", if in_time == start_time, no left trim
        cd, the cut duration
        wl, the whole length of the unedited clip
        path, the clip file path (string)
        name (string)
    NB: Clip.timeline_pos (the position on the global timeline) is not set here but latter computed from summing cut times
    """
    def _float_time(json_rationaltime):
        # returns a time in seconds (float)
        return json_rationaltime['value']/json_rationaltime['rate']
    av_range = jsoncl['media_references']['DEFAULT_MEDIA']['available_range']
    src_rg = jsoncl['source_range']
    st = av_range['start_time']
    In = src_rg['start_time']
    cd = src_rg['duration']
    wl = av_range['duration']
    path = jsoncl['media_references']['DEFAULT_MEDIA']['target_url']
    name = jsoncl['media_references']['DEFAULT_MEDIA']['name']
    return Clip(*[_float_time(t) for t in [st, In, cd, wl,]] + \
                    [name, path, 0, None])

def get_SND_dirs(snd_root):
    # returns all directories found under snd_root
    def _searchDirectory(cwd,searchResults):
        dirs = os.listdir(cwd)
        for dir in dirs:
            fullpath = os.path.join(cwd,dir)
            if os.path.isdir(fullpath):
                searchResults.append(fullpath)
                _searchDirectory(fullpath,searchResults)
    searchResults = []
    _searchDirectory(snd_root,searchResults)
    return searchResults

# logger.add(sys.stdout, filter=lambda r: r["function"] == "find_and_set_ISO_dir")
def find_and_set_ISO_dir(clip, SND_dirs):
    """
    SND_dirs contains all the *_SND directories found in snd_root.
    This fct finds out which one corresponds to the clip
    and sets the found path to clip.ISOdir.
    Returns nothing.
    """
    c_option_arg = pathlib.Path(clip.path).stem
    logger.debug(f'c_option_arg {c_option_arg}')
    m = re.match(r'(.*)_v(\w{32})', c_option_arg) # 
    logger.debug(f'{c_option_arg} match (.*)v([AB]*) { m.groups() if m != None else None}')
    if m != None:
        c_option_arg = m.groups()[0]
    # /MyBigMovie/day01/leftCAM/card01/canon24fps01_SND -> canon24fps01_SND
    names_only = [p.name for p in SND_dirs]
    logger.debug(f'names-only {pformat(names_only)}')
    clip_stem_SND = f'{c_option_arg}_SND'
    if clip_stem_SND in names_only:
        where = names_only.index(clip_stem_SND)
    else:
        print(f'Error: OTIO file contains clip not in SYNCEDROOT: {c_option_arg} (check with mamconf --show)')
        sys.exit(0)
    complete_path = SND_dirs[where]
    logger.debug(f'found {complete_path}')
    clip.ISOdir = str(complete_path)

# logger.add(sys.stdout, filter=lambda r: r["function"] == "gen_lua_table")
def gen_lua_table(clips, show_tc):
    """
    returns a string defining a lua nested table
    top level: a sequence of clips
    a clip has keys: name, start_time, in_time, cut_duration, timeline_pos, files
    clip.files is a sequence of ISO wav files
    """
    def _list_ISO(dir): 
        iso_dir = pathlib.Path(dir)/'ISOfiles'
        ISOs = [f for f in iso_dir.iterdir() if f.suffix.lower() == '.wav']
        if not show_tc:
            ISOs = [f for f in ISOs if f.name[:2] != 'tc'] # no timecode
        sequence = '{'
        for file in ISOs:
            sequence += f'"{file}",\n'
        sequence += '}'
        return sequence
    def _cols(dir, hue_rnd): 
        iso_dir = pathlib.Path(dir)/'ISOfiles'
        ISOs = [f for f in iso_dir.iterdir() if f.suffix.lower() == '.wav']
        if not show_tc:
            ISOs = [f for f in ISOs if f.name[:2] != 'tc'] # no timecode
        stems = [str(f.stem).split('_')[0] for f in ISOs]
        cols = [rnd_col(s, hue_rnd) for s in stems]
        sequence = '{'
        for c in cols:
            sequence += f'{c},\n'
        sequence += '}'
        return sequence
    lua_clips = '{'
    random.seed()
    hue_rnd = random.random()
    for cl in clips:
        ISOs = _list_ISO(cl.ISOdir)
        colors = _cols(cl.ISOdir, hue_rnd)
        logger.debug(f'colors: {colors}')
        logger.debug(f'ISOs {ISOs}')
        # logger.debug(f'sequence {ISOs}')
        clip_table = f'{{colors = {colors}, name="{cl.name}", start_time={cl.start_time}, in_time={cl.in_time}, cut_duration={cl.cut_duration}, timeline_pos={cl.timeline_pos}, files={ISOs}}}'
        lua_clips += f'{clip_table},\n'
        logger.debug(f'clip_table {clip_table}')
    lua_clips += '}'
    return lua_clips
    
# logger.add(sys.stdout, filter=lambda r: r["function"] == "read_OTIO_file")
def read_OTIO_file(f):
    """
    returns framerate and a list of Clip instances parsed from
    the OTIO file passed as (string) argument f;
    warns and exists if more than one video track.
    """
    with open(f) as fh:
        oti = json.load(fh)
    video_tracks = [tr for tr in oti['tracks']['children'] if tr['kind'] == 'Video']
    # removing empty video tracks
    video_tracks = [tr for tr in video_tracks if len(tr['children']) != 1]
    if len(video_tracks) > 1:
        print(f"Can only process timeline with one video track, this one has {len(video_tracks)}. Bye.")
        sys.exit(0)
    video_track = video_tracks[0]
    # remove transitions, keep OTIO_SCHEMA == Clip.2 only [TODO] remove GAP
    otio_clips = [e for e in video_track['children'] if e['OTIO_SCHEMA'] == 'Clip.2' ]
    clips = [clip_info_from_json(e) for e in otio_clips]
    # check each clip has a different file (cant have doublon, warn user)
    files = [cl.path for cl in clips]
    if len(set(files)) != len(clips):
        print(f'Error: some clips are used more than once in the timeline "{f}".')
# duplicate them on the filesystem, re-edit and rerun, bye.')
        counter = collections.Counter(files)
        reps_stats = {key: value for key, value in counter.items() if value > 1}
        print(f"The duplicates are {reps_stats}")
        rep_files = list(reps_stats.keys())
        for file in rep_files:
            print(f'Here are the clips for the duplicated file "{pathlib.Path(file).name}":')
            rep_clips = [cl for cl in clips if cl.path == file]
            print(rep_clips)
        print('Sorry for this limitation: the workaround is to duplicate the original clip ')
        print('add it to the NLE media pool and replace it on the timeline.')
        print('The ISOs files in SNDROOT should be duplicated too, with the same new name.')
        sys.exit(0)
    # compute each clip global timeline position
    clip_starts = [0] + list(itertools.accumulate([cl.cut_duration for cl in clips]))[:-1]
    # Reaper can't handle negative item position (for the trimmed part)
    # so starts at 1:00:00
    clip_starts = [t + 3600 for t in clip_starts]
    logger.debug(f'clip_starts: {clip_starts}')
    for time, clip in zip(clip_starts, clips):
        clip.timeline_pos = time
    logger.debug(f'clips: {pformat(clips)}')
    return int(oti['global_start_time']['rate']), clips

def build_reaper_render_action(wav_destination):
    directory = wav_destination.absolute().parent
    return f"""\nreaper.GetSetProjectInfo_String(0, "RENDER_FILE","{directory}",true)
reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN","{wav_destination.name}",true)
reaper.SNM_SetIntConfigVar("projintmix", 4)
reaper.Main_OnCommand(40015, 0)
"""

def InsertMedia(where, file):

    return f"""\nreaper.SetEditCurPos({where}, false, false)
reaper.InsertMedia("{file}", 1 )
local tr = reaper.GetTrack(0,reaper.CountTracks()-1)
reaper.GetSetMediaTrackInfo_String( tr, "P_NAME","video {file.stem}", true)
"""

# logger.add(sys.stdout, filter=lambda r: r["function"] == "complete_clip_path")
def complete_clip_path(c_option_arg, synced_proj):
    # scan synced_proj for a path containing c_option_arg
    # and return it
    match = []
    for (root,dirs,files) in os.walk(synced_proj):
        for f in files:
            p = pathlib.Path(root)/f
            if p.is_symlink() or p.suffix == '.reapeaks':
                continue
            # logger.debug(f'{f}')
            if c_option_arg in f.split('.')[0]: # match XYZvA.mov
                match.append(p)
    logger.debug(f'matches {match}')
    if len(match) > 1:
        print(f'Warning, some filenames collide:')
        [print(m) for m in match]
        print('Bye.')
        sys.exit(0)
    if len(match) == 0:
        print(f"Error, didn't find any clip containing *{c_option_arg}*. Bye.")
        sys.exit(0)
    return match[0]

def find_mode_from_args(movie_file, clip_names, frames_per_second, clips):
    """
    a) mamreap cut28.otio cut28.mov -> INTERCLIP_ALL if same lengths
    b) mamreap cut28.otio -> INTERCLIP_ALL
    c) mamreap -c 8064 -> INTRACLIP (not here)
    d) mamreap cut28.otio cut28.mov -> INTERCLIP_SOME if lengths differ
    e) mamreap cut28.otio cut28.mov 8064 ps01 -> INTERCLIP_SOME 
    f) mamreap cut28.otio 8064 ps01  -> INTERCLIP_SOME
    """
    if len(clip_names) == 2: # case e) + f)
        return mamdav.Modes.INTERCLIP_SOME ####################################
    if movie_file != None:
        movie_duration = float(ffmpeg.probe(movie_file)['format']['duration'])
    else:
        movie_duration = 0
    last_clip = clips[-1]
    otio_duration = last_clip.timeline_pos + last_clip.cut_duration - 3600
    otio_duration = rounded_int(otio_duration*frames_per_second)
    movie_duration = rounded_int(movie_duration*frames_per_second)
    logger.debug(f'movie_duration: {movie_duration} fr; otio_duration: {otio_duration} fr.')
    if otio_duration == movie_duration: # case a)
        return mamdav.Modes.INTERCLIP_ALL ######################################
    if movie_duration > otio_duration:
        print(f'Error: movie is longer than otio timeline {(movie_duration, otio_duration)}, bye.')
        sys.exit(0)
    if movie_duration == 0: # no mov file and
        if len(clip_names) == 0: # no clips, case b) 
            # so it's whole length
            return mamdav.Modes.INTERCLIP_ALL ##################################
    else: # mov shorter, case d)
        return mamdav.Modes.INTERCLIP_SOME #####################################
    # why here? all cases have been covered...
    print('Error finding mamreap mode from arguments...bye.')
    sys.exit(0)

def clip_from_abbr(otio_clips, abbr):
    clip = [cl for cl in otio_clips if abbr in cl.name]
    if len(clip) == 0:
        print(f'Error: didnt find clip {abbr} in otio file, bye.')
        sys.exit(0)
    if len(clip) > 1:
        print(f'Error: find more than on clip for {abbr} in otio file, bye.')
        for cl in clip:
            print(f'name: "{cl.name}" file: "{cl.path}"')
        sys.exit(0)
    else:
        return clip[0]

# logger.add(sys.stdout, filter=lambda r: r["function"] == "clip_subset")
def clip_subset(clips, movie_file, clip_names_abbr, fps):
    # find clip subset that recoup movie_file and/or clip_names_abbr
    def make_fr(fps):
        return lambda val: rounded_int(val*fps)
    fr = make_fr(fps)
    if len(clip_names_abbr) == 2:
        first_clip, last_clip = [clip_from_abbr(clips, a) for a in clip_names_abbr]
        fr_A = fr(first_clip.timeline_pos)
        fr_B = fr(last_clip.timeline_pos)
        logger.debug(f'first_clip, last_clip:')
        logger.debug(f'{first_clip.path} fr{fr_A}, {last_clip.path} fr{fr_B}')
        sub = [c for c in clips if fr(c.timeline_pos) >= fr_A and fr(c.timeline_pos) <= fr_B]
        logger.debug(f'sub : {sub}')
        return sub

# logger.add(sys.stdout, filter=lambda r: r["function"] == "main")
def main():
    otio_file, movie_file, clip_names, exit_flag, show_tc = parse_otio_args()
    logger.debug('otio_file, movie_file, clip_names, exit_flag:')
    logger.debug(f'{otio_file}, {movie_file}, {clip_names}, {exit_flag}.')
    # def _where(a,x):
    #     # find in which clip time x (in seconds) does fall.
    #     n = 0
    #     while n<len(a):
    #         if a[n].timeline_pos > x:
    #             break
    #         else:
    #             n += 1
    #     return n-1
    if len(clip_names) == 1:
        mode = mamdav.Modes.INTRACLIP
    else:
        # INTERCLIP_ALL or INTERCLIP_SOME
        frames_per_second, clips = read_OTIO_file(otio_file)
        mode = find_mode_from_args(movie_file, clip_names, frames_per_second, clips)
    logger.debug(f'mode: {mode}')
    raw_root, synced_root, snd_root, proxies = mamconf.get_proj(False)
    proj_name = pathlib.Path(raw_root).stem
    synced_proj = pathlib.Path(synced_root)/proj_name
    logger.debug(f'proj_name {proj_name}')
    logger.debug(f'will search {snd_root} for ISOs')
    all_SNDROOT_dirs = [pathlib.Path(f) for f in get_SND_dirs(snd_root)]
    # keep only XYZ_SND dirs
    SND_dirs = [p for p in all_SNDROOT_dirs if p.name[-4:] == '_SND']
    logger.debug(f'SND_dirs {pformat(SND_dirs)}')
    match mode:
        case mamdav.Modes.INTRACLIP:
            # e.g.: send-to-sound DSC087
            logger.debug('Modes.INTRACLIP, intraclip sound edit, clips will have one clip')
            # traverse synced_root to find clip path
            clip_path = complete_clip_path(clip_names[0], synced_proj)
            clip_stem = mamdav._vid_stem(clip_path)
            probe = ffmpeg.probe(clip_path)
            duration = float(probe['format']['duration'])
            clips = [Clip(
                        start_time=0,
                        in_time=0,
                        cut_duration=duration,
                        whole_duration=duration,
                        name=clip_stem,
                        path=clip_path,
                        timeline_pos=3600,
                        ISOdir='')]
            # [find_and_set_ISO_dir(clip, SND_dirs) for clip in clips]
            print(f'For video clip: \n{clip_path}\nfound audio in:\n{clips[0].ISOdir}')
        case mamdav.Modes.INTERCLIP_SOME:
            # [TODO]
            # e.g.: mamreap -p cut27.otio cut27.mov
            # clips = clip_subset(clips, movie_file, clip_names, frames_per_second)
            pass
        case mamdav.Modes.INTERCLIP_ALL:
            # e.g.: send-to-sound cut27.otio
            logger.debug('Modes.INTERCLIP_ALL, interclip sound edit, filling up ALL clips')
    [find_and_set_ISO_dir(clip, SND_dirs) for clip in clips]
    logger.debug(f'clips with found ISOdir: {pformat(clips)}')
    lua_clips = gen_lua_table(clips, show_tc)
    track_name = pathlib.Path(otio_file).stem
    lua_clips = lua_clips + f'\ntimeline_name = "{track_name}"'
    logger.debug(f'lua_clips {lua_clips}')
    # title = "Load MyBigMovie Audio.lua" either Modes
    title = f'Load {pathlib.Path(raw_root).name} Audio'
    script_path = pathlib.Path(REAPER_SCRIPT_LOCATION)/f'{title}.lua'
    Lua_script_pre, _ , Lua_script_post = REAPER_LUA_CODE.split('--cut here--')
    if movie_file == None:
        movie_scrpt = ''
    else:
        pr = ffmpeg.probe(movie_file)
        m = re.match(r".*timecode': '(\d\d):(\d\d):(\d\d).(\d\d)", str(pr))
        if m == None:
            print(f'Warning, no timcode found for movie {movie_file}')
            print('it will be placed at 01:00:00:00')
            HH,MM,SS,FF = [1,0,0,0]
        else:
            HH,MM,SS,FF = [int(e) for e in m.groups()]
            logger.debug(f'movie {movie_file} timecode: {(HH,MM,SS,FF)}')
        where = HH*3600  + MM*60 + SS + FF/frames_per_second
        movie_scrpt = InsertMedia(where, pathlib.Path(movie_file).resolve())
    script = Lua_script_pre + 'clips=' + lua_clips + Lua_script_post + movie_scrpt
    if is_windows:
         escaped_script = script.replace("\\", "\\\\")
         script = escaped_script
    with open(script_path, 'w') as fh:
        fh.write(script)
    print(f'Wrote ReaScripts "{script_path.stem}"', end=' ')
    if mode == mamdav.Modes.INTRACLIP:
        render_destination = pathlib.Path(clips[0].ISOdir)/f'{clip_stem}_mix.wav'
    else:
        logger.debug('render for mode all clips')
        op = pathlib.Path(otio_file)
        render_destination = op.parent/f'{op.stem}_mix.wav'
        logger.debug(f'render destination {render_destination}')
    logger.debug(f'will build rendering clip with dest: {render_destination}')
    lua_code = build_reaper_render_action(render_destination)
    if render_destination.exists():
        render_destination.unlink()
    logger.debug(f'clip\n{lua_code}')
    script_path = pathlib.Path(REAPER_SCRIPT_LOCATION)/f'Render Movie Audio.lua'
    if is_windows:
         escaped_script = lua_code.replace("\\", "\\\\")
         lua_code = escaped_script
    with open(script_path, 'w') as fh:
        fh.write(lua_code)
    print(f'and "{script_path.stem}" in directory \n"{REAPER_SCRIPT_LOCATION}"')
    print(f'Reaper will render audio to "{render_destination.absolute()}"')
    if mode in [mamdav.Modes.INTERCLIP_ALL, mamdav.Modes.INTERCLIP_SOME]:
        print(f'Warning: once saved, "{render_destination.name}" wont be of any use if not paired with "{op.name}", so keep them in the same directory.')
    if not exit_flag:
        # wait for mix and lauch mamdav
        print('Go editing in Reaper...')
        def _not_there_is_growing(dest, old_size):
            there = dest.exists()
            if there:
                new_size = dest.stat().st_size
                is_growing = new_size > old_size
            else:
                is_growing = False
                new_size = 0
            return there, is_growing, new_size
        with Progress(transient=True) as progress:
            task = progress.add_task(f"[green]Waiting for {render_destination.name}...", total=None)
            old_size = 0
            while True:
                there, is_growing, new_size = \
                     _not_there_is_growing(render_destination, old_size)
                if there and not is_growing:
                    break
                else:
                    old_size = new_size if there else 0
                time.sleep(1)
            progress.stop()
        time.sleep(3) # finishing writing?
        print(f'saw {render_destination.name}: ')
        # print('go mamdav!')
        wav_path = render_destination
        movie_path = None
        otio_path = op if mode != mamdav.Modes.INTRACLIP else None
        mamdav.go(mode, otio_path, movie_path, wav_path)



if __name__ == '__main__':
    main()


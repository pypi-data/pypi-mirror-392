from .hy3 import load as hy3_load
from .sd3 import load as sd3_load
from .yaml import load as yaml_load
from .scb import load as scb_load
from .ev3 import load as ev3_load
import urllib.request, zipfile, io

def load(filename, fo=None):
    """
    Load a swim results file and return a dictionary object with the parsed contents.

    @param filename the filename or URL of the results file to parse
    @param fo the file object (optional) of the file to parse (if None, then filename will be opened)
    """
    if fo is None:
        if filename.startswith("http:") or filename.startswith("https:"):
            cio = io.BytesIO(urllib.request.urlopen(filename).read())
        else:
            with open(filename,"rb") as fo:
                cio = io.BytesIO(fo.read())
        fo = cio

    if filename.lower().endswith(".zip"):
        zfo = zipfile.ZipFile(fo)
        scb_files = []
        for zfn in zfo.namelist():
            if zfn.endswith(".sd3") or zfn.endswith(".hy3") or zfn.endswith(".ev3"):
                zio = io.BytesIO(zfo.read(zfn))
                return load(zfn,zio)
            elif zfn.lower().endswith(".scb"):
                scb_files.append(zfn)
        if len(scb_files)>0:
            meetinfo = scb_load([io.BytesIO(zfo.read(zfn)) for zfn in scb_files])
            build_events_from_entries(meetinfo)
            return meetinfo
    elif filename.lower().endswith(".sd3"):
        return sd3_load(fo)
    elif filename.lower().endswith(".hy3"):
        meetinfo = hy3_load(fo)
        build_events_from_entries(meetinfo)
        return meetinfo
    elif filename.lower().endswith(".ev3"):
        return ev3_load(fo)
    elif filename.lower().endswith(".yml"):
        meetinfo = yaml_load(fo)
        build_events_from_entries(meetinfo)
        return meetinfo
    raise ValueError("no valid file found for parsing")

def _event_key_from_event(event):
    if event['type'] is None:
        event_prefix="A"
    elif event['type']=='Prelim':
        event_prefix="B"
    elif event['type']=='Semi':
        event_prefix="C"
    elif event['type']=="Final":
        event_prefix="D"

    # pad some 0s on the event_str to make a lexicographic sort possible
    event_str = event['index']
    while len(event_str)<6:
        event_str = "0"+event_str
    return event_prefix+"-"+event_str

def _event_key_from_entry(entry):
    if 'event_type' not in entry:
        event_prefix="0"
    elif entry['event_type'] is None:
        event_prefix="A"
    elif entry['event_type']=='Prelim':
        event_prefix="B"
    elif entry['event_type']=="Semi":
        event_prefix="C"
    elif entry['event_type']=="Final":
        event_prefix="D"

    # pad some 0s on the event_str to make a lexicographic sort possible
    event_str = entry['event_index']
    while len(event_str)<6:
        event_str = "0"+event_str
    return event_prefix+"-"+event_str

def build_events_from_entries(meetinfo):
    if 'events' in meetinfo:
        return # don't do anything if it's already built
    meetinfo['events'] = []

    if 'entries' in meetinfo:
        events_by_key = {}
        for entry in meetinfo['entries']:
            try:
                event_key = _event_key_from_entry(entry)
                if event_key not in events_by_key:
                    events_by_key[event_key] = {
                        "index":entry['event_index'],
                        "date":entry.get('event_date',None),
                        "gender":entry['event_gender'],
                        "gendercode":entry['event_gendercode'],
                        "course":entry['event_course'],
                        "coursecode":entry['event_coursecode'],
                        "stroke":entry['stroke'],
                        "strokeshort":entry['strokeshort'],
                        "distance":entry['distance'],
                        "relay":entry['relay'],
                        "type":entry.get('event_type',None),
                        "eligibility":None,
                        "num_heats":None
                    }
                    event = events_by_key[event_key]

                    name = "%s %d %s"%(event['gender'],event['distance'],event['strokeshort'])
                    if entry['relay']:
                        name += " Relay"
                    event['name'] = name

                if entry['heat'] is not None:
                    if events_by_key[event_key]['num_heats'] is None or \
                            events_by_key[event_key]['num_heats']<entry['heat_number']:
                        events_by_key[event_key]['num_heats'] = entry['heat_number']
            except TypeError:
                print("invalid entry",entry)
                raise

        meetinfo['events'] = [events_by_key[event_key] for event_key in sorted([event_key for event_key in events_by_key.keys()])]
    
def populate_events_entries(meetinfo):
    _events_by_key = {}
    _swimmer_ids_to_swimmer = {}
    for swimmer in meetinfo['swimmers']:
        _swimmer_ids_to_swimmer[swimmer['swimmer_id']] = swimmer
    for event in meetinfo['events']:
        event['entries'] = []
        _events_by_key[_event_key_from_event(event)] = event
    if 'entries' in meetinfo:
        for entry in meetinfo['entries']:
            event = _events_by_key[_event_key_from_entry(entry)]
            entry = entry.copy()
            entry['swimmers'] = [_swimmer_ids_to_swimmer[sid] for sid in entry['swimmer_ids']]
            event['entries'].append(entry)

def populate_heats(event):
    event['heats'] = []
    heats_by_key = {}
    if 'entries' in event:
        for entry in event['entries']:
            if entry['heat'] is not None:
                if entry['heat_number'] not in heats_by_key:
                    heats_by_key[entry['heat_number']] = {
                        "heat":entry['heat'],
                        "heat_number":entry['heat_number'],
                        "entries":[]
                    }
                heats_by_key[entry['heat_number']]['entries'].append(entry)
        for heat_num in sorted([hnum for hnum in heats_by_key.keys()]):
            heats_by_key[heat_num]['entries'].sort(key=lambda e:e['lane'])
            event['heats'].append(heats_by_key[heat_num])
    return event

def get_lanes(meetinfo):
    if 'entries' in meetinfo:
        lanes = []
        for entry in meetinfo['entries']:
            if entry['lane'] is not None and entry['lane'] not in lanes:
                lanes.append(entry['lane'])
        lanes.sort()
        return lanes
    else:
        raise ValueError("meetinfo doesn't have entries")

from .util import *
import logging
logger = logging.getLogger(__name__)

HY3_STROKE_CODES = {
    "A":"Freestyle",
    "B":"Backstroke",
    "C":"Breaststroke",
    "D":"Butterfly",
    "E":"Individual Medley",
    "F":"Freestyle Relay",
    "G":"Medley Relay"
}
HY3_STROKE_CODES_SHORT = {
    "A":"Free",
    "B":"Back",
    "C":"Breast",
    "D":"Fly",
    "E":"IM",
    "F":"Free Relay",
    "G":"Medley Relay"
}
HY3_EVENT_GENDER_CODES = {
    "M":"Men",
    "F":"Women",
    "W":"Women",
    "B":"Boys",
    "G":"Girls",
    "X":"Mixed"
}
HY3_EVENT_COURSE_CODES = {
    "S":"SCM",
    "Y":"SCY",
    "L":"LCM"
}
HY3_EVENT_TYPE_CODES = {
    "P":"Prelim",
    "S":"Semi",
    "F":"Final",
}

SWIMMER_CODE_LENGTH=4

def _mmddyyyy_date_to_iso_date(ds):
    if len(ds)==8:
        return ds[4:8]+"-"+ds[0:2]+"-"+ds[2:4]
    else:
        return None

def load(fo):
    # starts with A1 instead of A0
    meetinfo = {"teams":[],"swimmers":[],"entries":[]}
    teams = meetinfo['teams']
    swimmers = meetinfo['swimmers']
    entries = meetinfo['entries']
    line = 0
    cur_swimmer = None
    cur_entry = None
    cur_team = None
    _swimmer_code_to_ids = {}
    _team_short_names = set()
    already_e2_submitted = False
    while ((record := fo.read(132))):
        line += 1
        try:
            rtype = record[0:2]
            if rtype == b'B1':
                meetinfo['name'] = record[2:47].decode('latin').strip()
                meetinfo['location'] = record[47:92].decode('latin').strip()
                startdate_str = record[92:100].decode('latin').strip()
                meetinfo['startdate'] = _mmddyyyy_date_to_iso_date(startdate_str)
                enddate_str   = record[100:108].decode('latin').strip()
                meetinfo['enddate'] = _mmddyyyy_date_to_iso_date(enddate_str)
            elif rtype == b"C1":
                cur_team = {
                    "short_name":record[2:7].decode('latin').strip(),
                    "name":record[7:37].decode('latin').strip(),
                }
                # don't add duplicates (some files have them...)
                if cur_team['short_name'] not in _team_short_names:
                    teams.append(cur_team)
                    _team_short_names.add(cur_team['short_name'])

            elif rtype == b"D1": # a swimmer record
                gender = record[2:3].decode('latin').strip()
                fname = record[28:48].decode('latin').strip()
                lname = record[8:28].decode('latin').strip()
                miname = record[68:69].decode('latin').strip()
                pfname = record[48:68].decode('latin').strip()
                swimmer_code = record[4:4+SWIMMER_CODE_LENGTH].decode('latin').lower() # don't strip, padding is part of the key
                swimmer_gendercode = record[2:3].decode('latin')
                swimmer_id = record[69:81].decode('latin').strip()
                birthday_str = record[88:96].decode('latin')
                swimmer_age = record[97:99].decode('latin').strip()
                if swimmer_age == "":
                    swimmer_age = None
                else:
                    swimmer_age = int(swimmer_age,10)

                cur_swimmer = {"name":"{}, {}".format(lname,pfname if pfname else fname),
                    "lastname":lname,"firstname":fname,
                    "gender":gender,
                    "swimmer_id":swimmer_id,
                    "middlei":miname,
                    "birthday":_mmddyyyy_date_to_iso_date(birthday_str),
                    "age":swimmer_age,
                    "team_short_name":cur_team['short_name'],
                    "preferredname":pfname}
                
                if swimmer_code in _swimmer_code_to_ids:
                    # duplicate! Check to make sure it appears to be the same
                    assert swimmer_id == _swimmer_code_to_ids[swimmer_code] 
                else:
                    # not duplicate, add to record
                    swimmers.append(cur_swimmer)
                    _swimmer_code_to_ids[swimmer_code] = swimmer_id

            elif rtype == b'E1': # individual entry record
                already_e2_submitted = False

                strokecode = record[21:22].decode('latin')
                #print("stroke",HY3_STROKE_CODES[strokecode])
                distance = int(record[15:21].decode('latin'))
                event_gendercode = record[14:15].decode('latin')
                if event_gendercode not in HY3_EVENT_GENDER_CODES:
                    logger.warning("unknown gender code %s",event_gendercode)
                #print("distance",repr(record[67:71]))
                #print("event #",record[72:76])
                event_num_str = record[38:42].decode('latin').strip()

                seed_coursecode = record[50:51].decode('latin').strip()
                if seed_coursecode in HY3_EVENT_COURSE_CODES:
                    seed_course = HY3_EVENT_COURSE_CODES[seed_coursecode]
                else:
                    seed_course = None

                #print("event #",event_num)
                # I'm not 100% sure this is the seed time field.
                # there are other time fields and I don't have a
                # good way to figure out which is what
                seed_time = record[42:50].decode('latin').strip()
                #print("possible seed time",seed_time)
                if seed_time and seed_time != "NT":
                    seed_time_ms = int(seed_time.replace('.',''),10)*10
                    if seed_time_ms == 0:
                        seed_time_ms = None
                        seed_time = None
                else:
                    seed_time = None
                    seed_time_ms = None

                cur_entry = {
                    "event_index":event_num_str,
                    "event_gendercode":event_gendercode,
                    "event_gender":HY3_EVENT_GENDER_CODES[event_gendercode] if event_gendercode in HY3_EVENT_GENDER_CODES else "Unknown",
                    "event_course":None,
                    "event_coursecode":None,
                    "event_typecode":None,
                    "event_type":"Final", # is this the correct default?
                    "event_date":None,
                    "heat":None,
                    "heat_number":None,
                    "lane":None,
                    "stroke":HY3_STROKE_CODES[strokecode],
                    "strokeshort":HY3_STROKE_CODES_SHORT[strokecode],
                    "distance":distance,
                    "seed_time":seed_time,
                    "seed_course":seed_course,
                    "seed_coursecode":seed_coursecode,
                    "seed_time_ms":seed_time_ms,
                    "seed_time_str":swimtimefmt(seed_time_ms),
                    "swimmer_ids":[cur_swimmer['swimmer_id']],
                    "result_time_ms":None,
                    "result_time_str":None,
                    "relay":False,
                    "dq":False,
                    "points":None,
                    "place":None,
                    "splits":None,
                }

                points = record[62:68].decode('latin').strip()
                if points:
                    points = float(points)
                else:
                    points = None
                cur_entry['points'] = points

                entries.append(cur_entry)

            elif rtype == b'E2': # continuation of an entry
                # there can be multiple E2 lines per E1 which are multiple entries in each event (usually for prelim,semis,finals)
                # we should probably make the seed time for semis be the prelim result time. and the result time for finals be the
                # semis result time. TODO!

                if already_e2_submitted: # we need to duplicate the entry and add it to the list
                    cur_entry = cur_entry.copy()
                    entries.append(cur_entry)
                already_e2_submitted = True

                event_type = record[2:3].decode('latin').strip()
                cur_entry['event_typecode'] = event_type
                if event_type in HY3_EVENT_TYPE_CODES:
                    cur_entry['event_type'] = HY3_EVENT_TYPE_CODES[event_type]
                else:
                    cur_entry['event_type'] = "Final" # Is this the correct default?
                cur_entry['event_typecode'] = event_type
                cur_entry['heat'] = record[20:23].decode('latin').strip()
                cur_entry['heat_number'] = int(cur_entry['heat'],10)
                cur_entry['lane'] = record[23:26].decode('latin').strip()

                event_datestr = record[87:95].decode('latin').strip()
                cur_entry['event_date'] = _mmddyyyy_date_to_iso_date(event_datestr)

                cur_entry['event_coursecode'] = record[11:12].decode('latin').strip()
                if cur_entry['event_coursecode'] in HY3_EVENT_COURSE_CODES:
                    cur_entry['event_course'] = HY3_EVENT_COURSE_CODES[cur_entry['event_coursecode']]
                else:
                    logger.warning("no course found? %s",repr(record))

                # results
                cur_entry['result_time'] = record[4:11].decode('latin').strip()
                if cur_entry['result_time'] == "" and cur_entry['result_time']!="0.00":
                    cur_entry['result_time'] = None
                    cur_entry['result_time_ms'] = None
                else:
                    cur_entry['result_time_ms'] = int(cur_entry['result_time'].replace('.',''),10)*10

                cur_entry['dq'] = (record[12:13].decode('latin') == "Q")

                place = record[31:33].decode('latin').strip()
                if place == "":
                    cur_entry['place'] = None
                else:
                    cur_entry['place'] = int(place,10)
                
                #print("prelim heat #",record[124:126])
                #print("prelim lane #",record[126:128])
                #print("finals heat #",record[128:130])
                #print("finals lane #",record[130:132])
                #print(repr(record))

            elif rtype == b'F1': # relay entry
                strokecode = record[21:22].decode('latin')
                #print("stroke",HY3_STROKE_CODES[strokecode])
                distance = int(record[15:21].decode('latin'))
                event_gendercode = record[14:15].decode('latin')
                #print("distance",repr(record[67:71]))
                #print("event #",record[72:76])
                relayname = record[2:11].decode('latin').strip()

                event_num_str = record[38:42].decode('latin').strip()

                seed_coursecode = record[50:51].decode('latin').strip()
                if seed_coursecode in HY3_EVENT_COURSE_CODES:
                    seed_course = HY3_EVENT_COURSE_CODES[seed_coursecode]
                else:
                    seed_course = None

                # I'm not 100% sure this is the seed time field.
                # there are other time fields and I don't have a
                # good way to figure out which is what
                seed_time = record[42:50].decode('latin').strip()
                #print("possible seed time",seed_time)
                seed_time_ms = int(seed_time.replace('.',''),10)*10
                if seed_time_ms == 0:
                    seed_time_ms = None
                    seed_time = None

                cur_entry = {
                    "event_index":event_num_str,
                    "heat":None,
                    "heat_number":None,
                    "lane":None,
                    "event_gendercode":event_gendercode,
                    "event_gender":HY3_EVENT_GENDER_CODES[event_gendercode] if event_gendercode in HY3_EVENT_GENDER_CODES else "Unknown",
                    "event_course":None,
                    "event_coursecode":None,
                    "event_typecode":None,
                    "event_type":"Final", # is this the correct default?
                    "stroke":HY3_STROKE_CODES[strokecode],
                    "strokeshort":HY3_STROKE_CODES_SHORT[strokecode],
                    "distance":distance,
                    "seed_time":seed_time,
                    "seed_course":seed_course,
                    "seed_coursecode":seed_coursecode,
                    "seed_time_ms":seed_time_ms,
                    "seed_time_str":swimtimefmt(seed_time_ms),
                    "result_time_ms":None,
                    "result_time_str":None,
                    "relay":True,
                    "teamname":relayname,
                    "swimmer_codes":[],
                    "dq":False,
                    "points":None,
                    "place":None,
                    "splits":None,
                }

                points = record[62:68].decode('latin').strip()
                if points:
                    points = float(points)
                else:
                    points = None
                cur_entry['points'] = points

                entries.append(cur_entry)

            elif rtype == b'F2':
                # TODO: update this in case relays have prelims, semis, final (as per E2 records above)
                event_type = record[2:3].decode('latin').strip()
                cur_entry['event_typecode'] = event_type
                if event_type in HY3_EVENT_TYPE_CODES:
                    cur_entry['event_type'] = HY3_EVENT_TYPE_CODES[event_type]
                else:
                    cur_entry['event_type'] = None
                cur_entry['event_typecode'] = event_type

                cur_entry['heat'] = record[20:23].decode('latin').strip()
                cur_entry['heat_number'] = int(cur_entry['heat'],10)
                cur_entry['lane'] = record[23:26].decode('latin').strip()
                #print(cur_entry['heat'])
                #print(cur_entry['lane'])

                event_datestr = record[102:110].decode('latin').strip()
                cur_entry['event_date'] = _mmddyyyy_date_to_iso_date(event_datestr)
                
                cur_entry['event_coursecode'] = record[11:12].decode('latin').strip()
                if cur_entry['event_coursecode'] in HY3_EVENT_COURSE_CODES:
                    cur_entry['event_course'] = HY3_EVENT_COURSE_CODES[cur_entry['event_coursecode']]
                else:
                    logger.warning("no course found in record? %s",repr(record))

                # results
                cur_entry['result_time'] = record[5:11].decode('latin').strip()
                if cur_entry['result_time'] == "" and cur_entry['result_time']!="0.00":
                    cur_entry['result_time'] = None
                    cur_entry['result_time_ms'] = None
                else:
                    cur_entry['result_time_ms'] = int(cur_entry['result_time'].replace('.',''),10)*10

                cur_entry['dq'] = (record[12:13].decode('latin') == "Q")

                place = record[31:33].decode('latin').strip()
                if place == "":
                    cur_entry['place'] = None
                else:
                    cur_entry['place'] = int(place,10)

            elif rtype == b'F3':
                # load swimmers for the relay
                swimmercodes = []
                for swimmerposn in [4,17,30,43,56,69,82,95]:
                    swimmercode = record[swimmerposn:swimmerposn+SWIMMER_CODE_LENGTH].decode('latin').lower()
                    if swimmercode.strip():
                        swimmercodes.append(swimmercode)
                cur_entry['swimmer_codes'] = swimmercodes

            elif rtype == b'G1':
                if cur_entry['splits'] is None:
                    cur_entry['splits'] = []
                for startidx in range(3,112,11):
                    laps = record[startidx:startidx+2].decode('latin').strip()
                    if not laps:
                        break # no more splits
                    laps = int(laps)
                    splittime = record[startidx+2:startidx+10].decode('latin').strip()
                    splittime = int(splittime.replace('.',''))*10 # convert to ms
                    cur_entry['splits'].append((laps*25,splittime))
        except:
            logger.exception("exception on line %d data %s", line, repr(record))
            raise

    # Make a mapping for all entries to swimmer IDs (which are more unique and useful than the swimmer codes)
    # While this is isn't listed with every entry, this is a helpful enough item to save for database lookups
    # that we're going to add it for convenience
    for entry in meetinfo['entries']:
        if 'swimmer_codes' in entry: # only relays have this
            entry['swimmer_ids'] = [_swimmer_code_to_ids[code] for code in entry['swimmer_codes']]
            del entry['swimmer_codes']

    return meetinfo
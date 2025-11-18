import yaml
from .hy3 import HY3_EVENT_COURSE_CODES, HY3_EVENT_GENDER_CODES, HY3_STROKE_CODES, HY3_STROKE_CODES_SHORT
from .util import swimtime_strtoms

def load(fo):
    ydata = yaml.load(fo,Loader=yaml.BaseLoader)
    meetinfo = {"entries":[],"location":""}

    for fieldname in ['name','location','startdate','enddate','qualifying_age_date','qualifying_date_from','qualifying_date_to']:
        if fieldname in ydata:
            meetinfo[fieldname] = str(ydata[fieldname]).strip()

    if 'events' in ydata:
        meetinfo['events'] = []
        for event in ydata['events']:
            eventdata = {}
            meetinfo['events'].append(eventdata)
            
            if 'event' in event:
                eventdata['index'] = str(event['event'])
            elif 'index' in event:
                eventdata['index'] = str(event['index'])
            else:
                eventdata['index'] = None

            eventdata['date'] = event['date'] if 'date' in event else None
            
            if 'gender' in event:
                gender_str = event['gender']
                event_gendercode = None
                for gkey,gvalue in HY3_EVENT_GENDER_CODES.items():
                    if gender_str.lower() == gvalue.lower() or gender_str.lower()==gkey.lower():
                        gender_str = gvalue # normalize gender code
                        event_gendercode = gkey
                        break
                eventdata['gender'] = gender_str
                eventdata['gendercode'] = event_gendercode
            else:
                eventdata['gender'] = "Mixed"
                eventdata['gendercode'] = "X"

            for coursecode, course_str in HY3_EVENT_COURSE_CODES.items():
                if event['course'].upper() == coursecode or event['course'].upper() == course_str:
                    eventdata['course'] = course_str
                    eventdata['coursecode'] = coursecode
            
            eventdata['stroke'] = event['stroke']
            eventdata['strokeshort'] = None
            strokecode = None
            for scode, stroke_value in HY3_STROKE_CODES_SHORT.items():
                if event['stroke'].lower() == stroke_value.lower():
                    strokecode = scode
                    break
            for scode, stroke_value in HY3_STROKE_CODES.items():
                if event['stroke'].lower() == stroke_value.lower():
                    strokecode = scode
                    break
            if strokecode is not None:
                eventdata['stroke'] = HY3_STROKE_CODES[strokecode]
                eventdata['strokeshort'] = HY3_STROKE_CODES_SHORT[strokecode]
            
            if not isinstance(event['distance'], int):
                eventdata['distance'] = int(event['distance'],10)

            eventdata['relay'] = bool(event.get('relay',False))
            eventdata['type'] = event.get('type',"Final")

            if 'eligibility' in event:
                eventdata['eligibility'] = []
                for e in event['eligibility']:
                    eldata = {
                        "age_from":int(e.get('age_from',0)),
                        "age_to":int(e.get('age_to',109)),
                    }
                    eventdata['eligibility'].append(eldata)

                    # inherit default course from event
                    eldata['course'] = eventdata['course']
                    if 'course' in e:
                        for coursecode, course_str in HY3_EVENT_COURSE_CODES.items():
                            if e['course'].upper() == coursecode or e['course'].upper() == course_str:
                                e['course'] = course_str

                    eldata['gender'] = eventdata['gender']
                    eldata['gendercode'] = eventdata['gendercode']
                    if 'gender' in e:
                        gender_str = e['gender']
                        e_gendercode = None
                        for gkey,gvalue in HY3_EVENT_GENDER_CODES.items():
                            if gender_str.lower() == gvalue.lower() or gender_str.lower()==gkey.lower():
                                gender_str = gvalue # normalize gender code
                                e_gendercode = gkey
                                break
                        eldata['gender'] = gender_str
                        eldata['gendercode'] = e_gendercode

                    eldata['time_ms'] = swimtime_strtoms(e['time']) if 'time' in e else int(e['time_ms'])

    # at the moment, we don't support loading entries from YAML, but we could. this was old code below
    # that was unused and didn't get updated to the new schema
    """         for entry in event['entries']:
            swimmer_codes = []
            for swimmer in entry['swimmers']:
                if (swimmer['team_short_name'],swimmer['name']) not in swimmers_by_team_and_name:
                    cur_swimmer = {"name":swimmer['name'],
                        "lastname":swimmer['name'],"firstname":swimmer['name'],
                        "swimmer_code":swimmer['swimmer_code'],
                        "middlei":None,
                        "birthday_str":None,
                        "age":None,
                        "team_short_name":swimmer['team_short_name'],
                        "preferredname":swimmer['name'], "entries":[]}
                    swimmers_by_team_and_name[(swimmer['team_short_name'],swimmer['name'])] = cur_swimmer
                    teams[swimmer['team_short_name']]['swimmers'].append(cur_swimmer)
                else:
                    cur_swimmer = swimmers_by_team_and_name[(swimmer['team_short_name'],swimmer['name'])]
                swimmer_codes.append(cur_swimmer['swimmer_code'])
            seed_time = swimtime_strtoms(entry['seed_time']) if entry['seed_time'] and entry['seed_time']!="null" else None
            cur_entry = {
                "event":int(event['event']),
                "event_number":int(event['event']),
                "event_gender":HY3_EVENT_GENDER_CODES[event_gendercode],
                "event_gendercode":event_gendercode,
                "stroke":HY3_STROKE_CODES[strokecode],
                "strokeshort":HY3_STROKE_CODES_SHORT[strokecode],
                "swimmer_codes":swimmer_codes,
                "heat":str(entry['heat']),
                "heat_number":int(entry['heat']),
                "lane":int(entry['lane']),
                "distance":int(event['distance']),
                "seed_time":entry['seed_time'],
                "seed_time_ms":seed_time,
                "seed_time_str":swimtimefmt(seed_time),
                "relay":bool(event['relay']),
            }
            teams[cur_swimmer['team_short_name']]['entries'].append(cur_entry)

    teams = [value for _,value in teams.items()] # convert to array
    """
    return meetinfo
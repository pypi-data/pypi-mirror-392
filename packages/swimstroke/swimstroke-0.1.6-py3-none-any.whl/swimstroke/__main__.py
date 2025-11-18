import sys
from .helpers import load, populate_events_entries, populate_heats
from .util import swimtimefmt
import logging
logging.basicConfig(level=logging.INFO)

for filename in sys.argv[1:]:
    print(filename)
    meetinfo = load(filename)
    #print(repr(meetinfo.keys()))

    populate_events_entries(meetinfo)
    for event in meetinfo['events']:
        populate_heats(event)
        print(event['index'],event['gender'],event['stroke'],event['distance'],event['course'],event['date'])
        if event['eligibility']:
            for elinfo in event['eligibility']:
                print(" * ",elinfo['gender'],elinfo['age_from'],"-",elinfo['age_to'],elinfo['course'],swimtimefmt(elinfo['time_ms']))
        for entry in event['entries']:
            #print(repr(entry))
            if entry['relay']:
                print(" * relay - ",entry['heat'],entry['lane'],entry['teamname'],', '.join([e['name'] for e in entry['swimmers']]),entry['event_type'],"** DISQUALIFIED **" if entry['dq'] else "")
            else:
                print(" * ",entry['heat'],entry['lane'],entry['swimmers'][0]['name'],swimtimefmt(entry['seed_time_ms']),entry['event_type'],"** DISQUALIFIED **" if entry['dq'] else "")


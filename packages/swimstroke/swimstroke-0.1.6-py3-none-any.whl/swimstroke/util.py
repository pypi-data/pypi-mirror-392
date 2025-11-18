def swimtimefmt(time_ms):
    if time_ms is None:
        return ""
    elif time_ms>=60000:
        return "%d:%02d.%02d"%(time_ms//60000, (time_ms//1000)%60, ((time_ms//10)%100))
    else:
        return "%d.%02d"%(time_ms//1000, ((time_ms//10)%100))

def format_result_time(result):
    course = result['course'] if 'course' in result else (result['event_course'] if 'event_course' in result else None)
    if course == "LCM":
        return swimtimefmt(result['result_time_ms'])+"L"
    elif course == "SCM":
        return swimtimefmt(result['result_time_ms'])+"S"
    elif course == "SCY":
        return swimtimefmt(result['result_time_ms'])+"Y"
    else:
        return swimtimefmt(result['result_time_ms'])

def swimtime_strtoms(time_str):
    if time_str is None or len(time_str)==0: return None
    if ':' in time_str:
        minutes, rest = time_str.split(':')
    else:
        minutes = "0"
        rest = time_str
    if '.' in rest:
        seconds, hundreths = rest.split(".")
        if len(hundreths)==1: # this is really tenths then
            hundreths += "0" # pad a zero onto the end
    else:
        seconds = rest
        hundreths = "0"
    return int(minutes,10)*60000 + int(seconds,10)*1000 + int(hundreths,10)*10
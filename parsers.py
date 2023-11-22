import re

investor_details_parser_regexes = [r'\("([^"]+)",([^)]+)\)', r'\(([^,]+),([^)]+)\)', r'\(([^,]+),(".*")\)']

def parse_investor_details(value, regexes=investor_details_parser_regexes, index=0):
    if index == 3:
        return None
    match = re.match(regexes[index], value)
    if match:
        return match.group(1).strip('"').strip(), match.group(2).strip('"').strip()
    else:
        return parse_investor_details(value, regexes, index+1)

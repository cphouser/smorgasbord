"""
extremely limited org parser

"""
HEADING_STRIP = ["'","/","*"]

def parseOrg(path):
    def parseHeadingPath(above_lines):
        heading_path = ''
        depth = 0
        for line in above_lines[::-1]:
            heading = line.strip()
            if heading and heading[0] == '*':
                #print(line, heading)
                if depth and depth <= line.count('*'):
                    continue
                else:
                    depth = line.count('*')
                heading = line
                for char in HEADING_STRIP:
                    heading = heading.replace(char, '')
                if heading_path:
                    heading_path = heading.strip() + '/' + heading_path
                else:
                    heading_path = heading.strip()
                if line.count('*') == 1:
                    break
        return heading_path

    lines = []
    headings = {}
    with open(path, 'r') as orgfile:
        lines = orgfile.readlines()
    for idx, line in enumerate(lines):
        if ':PROPERTIES:' in line:
            end = 0
            for end_idx, line2 in enumerate(lines[idx:]):
                if ':END:' in line2:
                    end = end_idx
                    break
            properties = {}
            for line2 in lines[idx+1:idx+end]:
                first_colon = line2.find(':') + 1
                second_colon = line2[first_colon+1:].find(':') + first_colon + 1
                property_key = line2[first_colon:second_colon]
                properties[property_key] = line2[second_colon+1:].strip()

            headings[parseHeadingPath(lines[:idx])] = properties 
    return headings

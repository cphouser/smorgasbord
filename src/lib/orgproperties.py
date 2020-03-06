"""
extremely limited org parser

"""
HEADING_STRIP = ["'","/","*",":"]

def parseOrg(path):
    """
    return a dict of all headings in the file with all properties as keys

    accepts an org file path and builds a flat dict of all headings in the file.
    subheading keys are prefixed by the key of their parent heading, separated by a '/'
    all key-value pairs in the properties drawer of the heading are stored at
    <heading>.properties. all tags are stored at <heading>.tags. characters in the
    global constant HEADING_STRIP will be removed from each heading in the returned
    object. headings without a properties drawer are skipped.
    """
    def parseHeadingPath(above_lines):
        def parseTags(line):
            tag_list = []
            tag = ':'
            tag_start = len(line) - 1
            header_end = 0
            for char in line[::-1]:
                tag_start = tag_start - 1
                if tag == ':':
                    if char == ' ' or char == '\n' or char == '\t':
                        continue
                    elif char != ':':
                        break
                    elif char == ':':
                        tag = ''
                        continue
                elif char == ':':
                    tag_list.append(tag);
                    tag = ''
                    header_end = tag_start
                else:
                    tag = char + tag
            #if tag_list:
                #print(line)
                #print(header_end)
                #print(tag_list)
            return header_end, tag_list
        heading_path = ''
        depth = 0
        head_line = ''
        tags = []
        tag_start_idx = -1
        for line in above_lines[::-1]:
            heading = line.strip()
            if heading and heading[0] == '*':
                if depth and depth <= line.count('*'):
                    continue
                else:
                    #if heading_path == '':
                    #    head_line = line
                    depth = line.count('*')
                h_tag_start, h_tag_list = parseTags(line)
                if h_tag_list:
                    tag_start_idx = h_tag_start
                    tags = h_tag_list
                heading = line[:tag_start_idx]
                tag_start_idx = -1

                for char in HEADING_STRIP:
                    heading = heading.replace(char, '')
                if heading_path:
                    heading_path = heading.strip() + '/' + heading_path
                else:
                    heading_path = heading.strip()
                if line.count('*') == 1:
                    break
        return {heading_path: {'tags': tags}}


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
            heading = parseHeadingPath(lines[:idx])
            #heading_tags = parseTags(lines[idx-1])
            #headings[heading_str] = {}
            #headings[heading_str]['tags'] = heading_tags
            headings.update(heading)
            headings[next(iter(heading))]['properties'] = properties
    return headings

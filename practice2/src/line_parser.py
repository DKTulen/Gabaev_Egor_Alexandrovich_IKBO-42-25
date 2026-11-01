def parse_line(line):
    parts = line.split()
    if not parts:
        return "", []
    return parts[0],parts[1:]

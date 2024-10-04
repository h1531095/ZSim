def convert_to_float(s):
    try:
        return float(s)
    except ValueError:
        return s

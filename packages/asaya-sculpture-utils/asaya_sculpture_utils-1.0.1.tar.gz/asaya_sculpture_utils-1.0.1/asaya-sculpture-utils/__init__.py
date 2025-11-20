def format_dimensions(height, width, depth, unit="cm"):
    return f"{height} × {width} × {depth} {unit}"

def calculate_volume(height, width, depth):
    return height * width * depth
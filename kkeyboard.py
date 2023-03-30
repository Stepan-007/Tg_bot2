def create_keyboard(variants):
    rows = int(len(variants) ** 0.5)
    cols = len(variants) // rows
    matrix = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(variants[i * cols + cols])
        matrix.append(row)
    return matrix

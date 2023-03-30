def create_keyboard(variants):
    rows = round(len(variants) ** 0.5)
    cols = round(len(variants) / rows)
    matrix = []
    counter = 0
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(variants[counter])
            counter += 1
            if counter == len(variants):
                break
        matrix.append(row)
    return matrix

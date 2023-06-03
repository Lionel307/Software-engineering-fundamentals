def generate(n):
    result = [0]
    if n >= 1:
        result.append(1)
    if n >= 2:
        result.append(1)
    for x in range(3, n):
        result.append(result[x - 1] + result[x - 2])
    return result

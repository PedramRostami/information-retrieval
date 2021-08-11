

def binary_search(array, item, indexing_function):
    first = 0
    last = len(array) - 1
    if last == first:
        if indexing_function(array, first) == item:
            return first
        return None
    middle = int((first + last) / 2)
    while first <= last:
        if indexing_function(array, middle) == item:
            return middle
        elif indexing_function(array, middle) < item:
            first = middle + 1
        else:
            last = middle - 1
        middle = int((first + last) / 2)
    return None


def linear_search(array, item, indexing_function):
    for i in range(len(array)):
        if item == indexing_function(array, i):
            return i
    return None

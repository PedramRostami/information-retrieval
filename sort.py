

def __heapify(array, n, i, sorting_function):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2

    if l < n and sorting_function(array[largest], array[l]):
        largest = l

    if r < n and sorting_function(array[largest], array[r]):
        largest = r

    if largest != i:
        array[i], array[largest] = array[largest], array[i]
        __heapify(array, n, largest, sorting_function)


def heapsort(array, sorting_function):
    n = len(array)
    for i in range(n // 2 - 1, -1, -1):
        __heapify(array, n, i, sorting_function)

    for i in range(n - 1, 0, -1):
        array[i], array[0] = array[0], array[i]
        __heapify(array, i, 0, sorting_function)
    return array

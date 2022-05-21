import json
import jsonpickle


def store_sudokus(sudokus):
    with open("sudokus.json", "w") as file:
        json.dump(sudokus, file)


def load_sudokus():
    try:
        with open("sudokus.json", "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def load_sudoku(i):
    return jsonpickle.decode(load_sudokus()[i])
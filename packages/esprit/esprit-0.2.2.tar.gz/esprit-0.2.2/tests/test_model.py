from esprit.model import SpreadsheetModel


def test_sort_by_column_string_and_number():
    model = SpreadsheetModel()
    model.rows = 3
    model.cols = 2
    model.metadata = {
        "title": "Test Sheet",
        "columns": [
            {"name": "Name", "type": "string"},
            {"name": "Score", "type": "number"},
        ],
    }
    model.cells = {}

    model.set_cell(0, 0, "Bravo")
    model.set_cell(1, 0, "Alpha")
    model.set_cell(2, 0, "Charlie")

    model.set_cell(0, 1, 200)
    model.set_cell(1, 1, 150)
    model.set_cell(2, 1, 175)

    model.sort_by_column(0, ascending=True)
    assert model.get_cell_raw(0, 0) == "Alpha"
    assert model.get_cell_raw(1, 0) == "Bravo"
    assert model.get_cell_raw(2, 0) == "Charlie"

    model.sort_by_column(1, ascending=False)
    assert model.get_cell_raw(0, 1) == 200
    assert model.get_cell_raw(1, 1) == 175
    assert model.get_cell_raw(2, 1) == 150


def test_sort_by_column_boolean_and_empty_rows():
    model = SpreadsheetModel()
    model.rows = 4
    model.cols = 1
    model.metadata = {
        "title": "Booleans",
        "columns": [{"name": "Decision", "type": "boolean"}],
    }
    model.cells = {}

    model.set_cell(0, 0, True)
    model.cells["1,0"] = False
    # Leave row 2 empty to ensure empties always sort last
    model.set_cell(3, 0, "yes")

    model.sort_by_column(0, ascending=True)
    sorted_values = [model.get_cell_raw(row, 0) for row in range(model.rows)]
    assert sorted_values == [False, True, "yes", None]

    model.sort_by_column(0, ascending=False)
    sorted_values = [model.get_cell_raw(row, 0) for row in range(model.rows)]
    assert sorted_values == [None, True, "yes", False]

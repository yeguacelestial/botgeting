import gspread

gc = gspread.service_account(filename=".config/gspread/service_account.json")


def retrieve_summary_data(worksheet_name: str, sheet_index: int):
    wks = gc.open(worksheet_name).get_worksheet(sheet_index)
    sheet_title = wks.title

    categorias = wks.col_values(6, value_render_option="UNFORMATTED_VALUE")
    gastado = wks.col_values(7, value_render_option="UNFORMATTED_VALUE")

    # TODO: Return this data within summary data
    restante = wks.col_values(8, value_render_option="UNFORMATTED_VALUE")
    limite = wks.col_values(9, value_render_option="UNFORMATTED_VALUE")

    summary_data = dict(zip(categorias, gastado))

    # Remove all zeroes
    summary_data = {k: v for k, v in summary_data.items() if v != 0}

    return summary_data, sheet_title

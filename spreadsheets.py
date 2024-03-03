from charts import generate_pie_chart

import gspread

gc = gspread.service_account(filename=".config/gspread/service_account.json")

# Open a sheet from a spreadsheet in one go
wks = gc.open("BUDGETING").get_worksheet(-2)

# Periodo inicio
print(wks.get("F2")[0][0])

# Periodo final
print(wks.get("G2")[0][0])

# Gastos por categoria
despensa = wks.get("G4", value_render_option="UNFORMATTED_VALUE")[0][0]
educacion = wks.get("G5", value_render_option="UNFORMATTED_VALUE")[0][0]
transporte = wks.get("G6", value_render_option="UNFORMATTED_VALUE")[0][0]
salud = wks.get("G7", value_render_option="UNFORMATTED_VALUE")[0][0]
salidas = wks.get("G8", value_render_option="UNFORMATTED_VALUE")[0][0]

total = wks.get("G9", value_render_option="UNFORMATTED_VALUE")[0][0]

# Generate pie chart
data = [despensa, educacion, transporte, salud, salidas]

pie_chart = generate_pie_chart(data)

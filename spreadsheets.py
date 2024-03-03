import gspread

gc = gspread.service_account()

# Open a sheet from a spreadsheet in one go
wks = gc.open("BUDGETING").sheet1

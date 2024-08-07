# botgeting
A Telegram bot that helps you to manage your personal finances from a Google Sheet.

The bot is expected to:

- Create:
  - A new spreadsheet associated to the Google account of the user
  - A new sheet with the current month and year
  - New CATEGORIA specified by the user (max: 12)
  - AHORROS specified by the user (max: 3)
  - TRANSACCIONES captured by the user

- Read:
  - How much the user has spent per CATEGORIA
  - How much the user has spent per TIPO DE PAGO
  - How much the user has saved per PORTAFOLIO and how much RENDIMIENTO has been earned from it
  - How much the user has spent in a specific period of time

- Update:
  - TRANSACCIONES (CONCEPTO, CATEGORIA, CUOTA(MXN), TIPO DE TRANSACCION; FECHA will be the date of the transaction)
  - CATEGORIA (NOMBRE, LÍMITE)
  - AHORROS (PORTAFOLIO, INVERTIDO, RENDIMIENTO - TOTAL and FECHA DE CAPTURA will be automatically updated)

- Delete:
  - **TRANSACCIONES**
  - CATEGORIA
  - AHORROS PORTAFOLIO
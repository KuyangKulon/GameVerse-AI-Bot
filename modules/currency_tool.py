from currency_converter import CurrencyConverter

c = CurrencyConverter()

def convert_currency(amount, from_currency, to_currency):
    try:
        result = c.convert(amount, from_currency.upper(), to_currency.upper())
        return f"💱 {amount:,.2f} {from_currency.upper()} = {result:,.2f} {to_currency.upper()}"
    except Exception as e:
        return f"⚠️ Gagal konversi: {e}. Pastikan kode mata uang benar (misal: USD, IDR, EUR, JPY)"

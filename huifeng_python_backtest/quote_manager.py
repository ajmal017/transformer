class QuoteManager:
    def __init__(self):
        self.quote_table = dict()

    def update_table(self, symbol, quote):
        self.quote_table[symbol] = quote

    def get_quote_table(self):
        return self.quote_table

    def get_quote(self, symbol):
        if symbol in self.quote_table:
            return self.quote_table[symbol]
        else:
            return None

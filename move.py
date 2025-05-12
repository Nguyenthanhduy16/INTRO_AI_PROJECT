class Move:

    def __init__(self, xfrom, yfrom, xto, yto):
        self.xfrom = xfrom
        self.yfrom = yfrom
        self.xto = xto
        self.yto = yto

    def equals(self, other_move):
        return (self.xfrom == other_move.xfrom and 
                self.yfrom == other_move.yfrom and
                self.xto   == other_move.xto   and
                self.yto   == other_move.yto)

    # Thêm __eq__ an toàn:
    def __eq__(self, other):
        from move import Move
        if not isinstance(other, Move):
            return False
        return self.equals(other)

    def to_string(self):
        return f"({self.xfrom}, {self.yfrom}) -> ({self.xto}, {self.yto})"

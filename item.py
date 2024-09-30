class Item:
    def __init__(self, name: str, suggested_by: str, highest_bid):
        self.name = name
        self.highest_bid = highest_bid
        self.suggested_by = suggested_by
        self.current_leader = suggested_by
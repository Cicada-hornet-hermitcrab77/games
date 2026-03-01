    def Spring.trigger(self, fighter):
        # Activate springs on direct contact, remove on_ground requirement
        if abs(fighter.x - self.x) < self.W + 14:
            self.activate(fighter)
        
        # Other existing code remains unchanged...
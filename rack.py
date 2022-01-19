


class Rack:
    """
        A rack contain a RM (Rack Manager) and UUTs
    """
    def hasRmIp(self):
        """ if the RM has the IP address
            return True if RM has IP.
        """
        if self.ts is not None:
            return self.ts.getLeaseIp(self.rmac)
            
        return None

    def __init__(self, rsn):
        self.rsn = rsn
        self.rmac = None                # RM's MAC
        self.ts =  None                 # Referce to Test Station
        self.uuts = []
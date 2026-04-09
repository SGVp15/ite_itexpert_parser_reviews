class Contact:
    def __init__(self, s: str):
        s = s.strip()
        block_s = s.split('\t')
        self.name: str = ''
        self.company: str = ''
        self.email: str = ''
        self.prof = ''
        try:
            self.name: str = block_s[0]
            self.company: str = block_s[1]
            self.email: str = block_s[2].lower()
            self.prof: str = block_s[3]
        except Exception:
            pass

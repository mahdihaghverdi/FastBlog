class Service:
    def __init__(self, repo, **kwargs):
        self.repo = repo
        for key, value in kwargs.items():
            setattr(self, key, value)

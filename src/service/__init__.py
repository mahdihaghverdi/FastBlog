from abc import abstractmethod, ABC


class BaseService:
    def __init__(self, repo):
        self.repo = repo


class BaseBusinessObject(ABC):
    @abstractmethod
    async def dict(self):
        raise NotImplementedError

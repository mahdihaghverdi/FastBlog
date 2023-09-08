from abc import abstractmethod, ABC


class BaseBusinessObject(ABC):
    @abstractmethod
    async def dict(self):
        raise NotImplementedError

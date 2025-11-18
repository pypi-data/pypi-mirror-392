from abc import ABC, abstractmethod


class ADFNode(ABC):

    @abstractmethod
    def to_json(self):
        ...

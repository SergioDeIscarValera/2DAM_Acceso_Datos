from abc import ABC, abstractmethod

class EmailServiceABC(ABC):
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str, html_cuerpo: str = None) -> bool:
        pass

    @abstractmethod
    async def send_verify_email(self, to: str, code:str) -> bool:
        pass
class User:
    """
    This class represents a user, it contains the name and email of the user.

    Attributes
    ----------
    name : str
        The name of the user.
    email : str
        The email of the user.

    Parameters
    ----------
    name : str
        The name of the user.
    email : str
        The email of the user.
    """

    __name: str
    __email: str

    def __init__(self, name: str, email: str):
        self.__name = name
        self.__email = email
    
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, email: str):
        self.__email = email

    def __str__(self) -> str:
        return f'{self.name} <{self.email}>'

    def __repr__(self) -> str:
        return f'{self.name} <{self.email}>'

    def __eq__(self, other: object) -> bool:
        return self.name == other.name and self.email == other.email

    def __hash__(self) -> int:
        return hash((self.name, self.email))


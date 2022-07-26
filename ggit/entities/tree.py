import hashlib
from typing import List, Tuple, Union

from ggit.entities.blob import Blob


class Tree:
    """
    This class represents a TREE object, an entity that abstracts a directory, 
    it can stores blobs and other trees. The main goal of the tree is to associate
    a filename and a mode to blobs and other trees.
    The file and directory modes are the same as UNIX file modes, but these are less
    flexible, the only available modes are:\n
    - 100644: regular file, read/write permission
    - 100755: regular file, read/write permission, execute permission
    - 120000: symbolic link
    - 040000: directory

    Attributes
    ----------
    items : List[Tuple[:class:`ggit.entities.blob.Blob` | :class:`ggit.entities.tree.Tree`, str, str]]
        The items of the tree, a list of tuples containing the item, its name and the mode.
    hash : str
        The hash of the tree.
    content : bytes
        The content of the tree, the actual string of bytes that will be hashed.
    length : int
        The length of the tree content.
    item_count : int
        The number of items in the tree, recursively, counting the tree itself
    """

    __items: List[Tuple[Union["Blob", "Tree"], str, str]]
    __hash: str
    __content: bytes
    __length: int

    def __init__(self, __items: List[Tuple[Union["Blob", "Tree"], str, str]] = []):
        self.__items = __items
        self.__hash = self.__calculate_hash()

    @property
    def items(self) -> List[Tuple[Blob, str, str]]:
        return self.__items

    @items.setter
    def items(self, items: List[Tuple[Union["Blob", "Tree"], str, str]]):
        self.__items = items
        self.__hash = self.__calculate_hash()

    def append_item(self, item: Union["Blob", "Tree"], name: str, mode: str):
        """
        Append a blob or tree to the tree.

        Parameters
        ----------
        item : :class:`Blob` | :class:`Tree`
            The item to append.
        name : str
            The name of the item.
        mode : str
            The mode of the item.
        """
        self.__items.append((item, name, mode))
        self.__hash = self.__calculate_hash()

    @property
    def content(self) -> str:
        return self.__content
    
    @property
    def length(self) -> int:
        return self.__length

    @property
    def hash(self) -> str:
        return self.__hash
    
    @property
    def item_count(self) -> int:
        count = 1
        for i in self.__items:
            if isinstance(i[0], Tree):
                count += i[0].item_count
            elif isinstance(i[0], Blob):
                count += 1
        return count

    def __calculate_hash(self) -> str:
        """
        Calculate the hash of the tree.

        Returns
        -------
        str
            The hash of the tree.
        """
        self.__items = sorted(self.__items, key=lambda item: item[1])
        content = b''
        for item in self.__items:
            content += item[2].lstrip('0').encode()
            content += b' '
            content += item[1].encode()
            content += b'\0'
            content += bytes.fromhex(item[0].hash)
        self.__content = content
        self.__length = len(content)
        return hashlib.sha1(b"tree " + str(len(content)).encode('ascii') + b"\0" + content).hexdigest()

    def __str__(self) -> str:
        return f"Tree: {self.__hash}"

    def __repr__(self) -> str:
        return f"Tree: {self.__hash}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Tree):
            return self.__hash == other.hash
        return False

    def __hash__(self) -> int:
        return self.__hash

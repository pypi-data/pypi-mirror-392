from bluepyll.core.bluepyll_element import BluePyllElement

class BluePyllScreen:
    def __init__(self, name: str, elements: dict[str, BluePyllElement] = {}):
        self.name = name
        self.elements: dict[str, BluePyllElement] = elements

    def add_element(self, element: BluePyllElement):
        self.elements[element.label] = element
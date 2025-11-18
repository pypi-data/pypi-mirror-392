# src/ipsumheroes/core.py
"""
core.py —  The base classes

These classes are the fundamental building blocks of the generator.py module.

classes:
    IpsumView: A string-like view of a generated sentence or paragraphs
    Luminary: Represents a historical or notable figure.
    Section: Represents a subordinate clause (section) within a sentence.
    Sentence: Represents a sentence within a generated text fragment.
"""

from dataclasses import dataclass
from typing import ClassVar
import textwrap

# -----------------------------------------------------------------------------
#   Class: Luminary
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Luminary:
    """
    Represents a historical or notable figure, created from a simple 6-field tuple.

    We sometimes call the great figures of the past heroes, although the truth is
    that not every great person is recognized as one.

    This class is used to convert tuples (e.g., from a topic dataset) into structured
    Luminary objects. Each field in the tuple maps to one of the following attributes:

    Attributes:
        name (str): The name of the person.
        role (str): Their profession or societal role.
        note (str): A notable achievement or description.
        region (str): The geographic region they are associated with.
        lifespan (str): A string representing their birth and death years.
        age (int): The age they reached (or estimated age).

    Class Attributes:
        annotation_fmt (str): A format string used to generate annotations or
            footnotes describing the Luminary.

    Note:
        These attribute names are descriptive but not functionally significant.
        They could have been named generically (e.g., `field_1`, ..., `field_6`),
        but are chosen to reflect the intent of the data fields.
    """

    name: str
    role: str
    note: str
    region: str
    lifespan: str
    age: int

    annotation_fmt: ClassVar[str] = (
        "{bullet}{name}; {role} - {note}\n{region}; {lifespan}, aged {age}"
    )

    # When you define a @dataclass with the frozen=True parameter, it
    # automatically includes both __hash__ and __eq__ methods, unless you
    # explicitly override them.

    @property
    def id_str(self):
        return f"{self.name} {self.role} {self.note} {self.region}"

    def __post_init__(self):
        if self.age is None:
            object.__setattr__(self, "age", "?")
            # self.__setattr__('age', '?') -> gives frozenerror

    def __call__(self):
        return self.make_footnote()

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.name == other.name
            and self.role == other.role
            and self.note == other.note
            and self.region == other.region
        )

    def __hash__(self):
        return hash(self.id_str)

    def make_footnote(
        self,
        wrapped: bool = True,
        width: int = 69,
        indent_first: int = 4,
        indent_next: int = 6,
        bullet_style: str = "- ",
        space: str = " ",
    ) -> str:
        """
        Returns a formatted annotation string representing this Luminary instance.

        The annotation is based on `self.annotation_fmt`, and the resulting string
        is formatted with indentation and optional line wrapping. This is typically
        used as a footnote or legend under a paragraph.

        Example:
            Given the Luminary fields:
            ("Julius Caesar", "General & Dictator", "Transformed Roman Republic",
            "Rome", "100–44 BCE", 56)

            The result would be:

                '   - Julius Caesar; General & Dictator; Transformed Roman Republic\n'
                '      Rome; 100–44 BCE, aged 56'

        Args:
            wrapped (bool): Whether to wrap long lines.
            width (int): Maximum line width when wrapping.
            indent_first (int): Indentation for the first line.
            indent_next (int): Indentation for all subsequent lines.
            bullet_style (str): The bullet styling char(s)
            space (str): A regular space or the HTML-entity '&nbsp;'

        Returns:
            str: The formatted annotation string.
        """
        text = self.annotation_fmt.format(
            name=self.name,
            role=self.role,
            note=self.note,
            region=self.region,
            lifespan=self.lifespan,
            age=self.age,
            bullet=bullet_style,
        )

        # the fmt contains a newline, this means multiple lines to wrap
        # reformat the text lines such a way that:
        #   - each line breaks at position of arg `width`
        #   - the first line has indentation (arg `indent_first`)
        #   - subsequent lines has indentation (arg `indent_next`)

        if wrapped:
            width = width - max(indent_first, indent_next)
        else:
            width = 1000000  # prevend wrapping

        all_lines = []
        for line in text.splitlines():
            # wrap each line of the annotation into 1 or multiple lines
            wrapped_lines = textwrap.wrap(
                line, width=width, break_on_hyphens=False, replace_whitespace=False
            )
            all_lines.extend(wrapped_lines)

        # all_lines now contains all wrapped lines
        # now indent all these lines with some spaces
        indented_lines = []
        indented_lines.append(space * indent_first + all_lines[0])
        for line in all_lines[1:]:
            indented_lines.append(space * indent_next + line)

        text = "\n".join(indented_lines)
        return text

    @classmethod
    def instance_factory(cls: type, topic_data: list):
        """
        Creates a list of Luminary instances from a list of 6-field tuples.

        Args:
            cls (type): The class to instantiate (typically Luminary).
            topic_data (list): A list of tuples, each containing six fields
                corresponding to the Luminary constructor arguments.

        Returns:
            list: A list of instantiated Luminary objects.
        """
        return [cls(*row) for row in topic_data]


# -----------------------------------------------------------------------------
#   Class:  Section
# -----------------------------------------------------------------------------


class Section(list):
    """
    Represents a subordinate clause (section) within a sentence.

    While a standard `list` could be used to store the words, using a Section
    instance provides a clearer and more explicit abstraction.
    """

    def __init__(self, words: list[str]) -> None:
        super().__init__(words)


# -----------------------------------------------------------------------------
#   Class: Sentence
# -----------------------------------------------------------------------------


class Sentence(list):
    """
    Represents a sentence within a generated text fragment.

    Each sentence is composed of one or more subordinate clauses (sections),
    which are separated by commas. These sections are represented by instances
    of the `Section` class, making the `Sentence` class a composition of multiple
    `Section` instances.

    Sentences may also be modified through interpolation with names of notable
    figures or other subjects (e.g., music). These names are defined by instances
    of the `Luminary` class.
    """

    def __init__(
        self, sections: list[Section], luminaries: list[Luminary], cfg
    ) -> None:
        """
        Initializes a Sentence instance composed of Section and Luminary objects.

        Args:
            sections (List[Section]): The subordinate clauses that make up the
            sentence.
            luminaries (Optional[List[Luminary]]): Optional list of Luminary
            objects used for interpolating names or topics into the sentence.
        """
        super().__init__(sections)
        self.cfg = cfg
        # self.text = self._format_text()
        self._luminaries = dict()
        self.luminaries = luminaries

    def _format_text(self) -> str:
        # Sentence object : [ [ 'word', 'word', 'word'] , [ 'word', 'word.  ' ] ]
        # not using the 'capitalize' builtin as this will lowercase the luminaries
        sections = [" ".join(section) for section in self]
        sentence = ", ".join(sections)
        sentence = "{first}{rest}".format(first=sentence[0].upper(), rest=sentence[1:])
        return sentence

    @property
    def sentence(self) -> str:
        """Returns a Sentence as a text string, first character uppercased.

        The sentence is not yet terminated with an interpunction character.
        """
        return self._format_text()

    @property
    def luminaries(self) -> list[Luminary]:
        """
        Returns the list of unique Luminary objects in the order in which they
        appear in the sentence.

        Returns:
            list[Luminary]: Ordered list of unique Luminary instances.
        """
        return list(self._luminaries.keys())

    @luminaries.setter
    def luminaries(self, luminaries: list[Luminary]):
        """
        Adds a list of Luminary objects to the existing collection.

        This setter ensures that the collection contains only unique Luminary
        instances.

        Args:
            luminaries (list[Luminary]): List of Luminary objects to add.
        """
        # We need a list of unique luminaries for a sentence
        # but the ordering must be kept intact.
        # Keeping track of unique luminaries while maintaining the
        # ordering of the instance: this can be done with a dict.

        for lum in filter(None, luminaries):
            if not isinstance(lum, Luminary):
                raise TypeError("Only type Luminary is allowed.")
            # Add the luminary to the dict.
            # We do not maintain some kind of value, None will do.
            self._luminaries[lum] = None

    def __len__(self) -> int:
        """
        Returns the number of words in the sentence.

        Returns:
            int: The total number of words.
        """
        return len([word for section in self for word in section])
        # return len(self.text.split())

    def __repr__(self) -> str:
        """
        Returns a string representation of this Sentence instance, showing key
        properties.

        Example:
            <Sentence: (sections=2, words=14, luminaries=0)>

        Note:
            The returned string is intended for debugging and is not suitable for
            recreating new instances.

        Returns:
            str: A formatted string describing the Sentence instance.
        """
        return (
            f"< {self.__class__.__name__}: (sections={super().__len__()}, "
            f"words={len(self)}, "
            f"luminaries={len(self.luminaries)}) >"
        )

    def __str__(self) -> str:
        """
        Returns the full text of the sentence.

        Returns:
            str: The sentence text.
        """
        return self.sentence


# -----------------------------------------------------------------------------
#   Class: IpsumView
# -----------------------------------------------------------------------------


class IpsumView(str):
    """A string-like view of generated sentences or paragraphs.

    Behaves exactly like a string (supports concatenation, formatting, etc.)
    but also keeps access to its underlying sentence-building blocks.
    """

    """A string-like view of generated ipsum text.

    Behaves exactly like a string (supports concatenation, formatting, etc.),
    but also exposes its underlying building blocks as lists:
     - Sentence objects (these includes the sections and the Luminary objects)
     - ipsum block: ipsum text as strings
     - annotation block: annotations text as string
    """

    def __new__(
        cls,
        text: str,
        sentences: list[Sentence],
        ipsum_block: list[str],
        annotation_block: list[str],
    ):
        # str is immutable → initialization must happen in __new__
        obj = super().__new__(cls, text)
        obj._sentences = sentences
        obj._ipsum_block = ipsum_block
        obj._annotation_block = annotation_block
        return obj

    def __repr__(self) -> str:
        return f"IpsumView(sentences={len(self._sentences)}, ipsum_block={len(self._ipsum_block)}, annotation_block={len(self._annotation_block)}, repr-text=\n{super().__repr__()})"

    @property
    def blocks(self) -> tuple[list[Sentence], list[str], list[str]]:
        """Return the raw building blocks (list1, list2, list3).

        These lists are also availble as separate properties.

        Returns (tuple[list[Sentence], list[str], list[str]]):
            A tuple with 3 fields:
            - a list with the raw Sentence objects
            - a list with the Ipsum textlines
            - a list with the annotation textlines
        """
        return self._sentences, self._ipsum_block, self._annotation_block

    @property
    def sentences(self) -> list[Sentence]:
        """Return the raw Sentence objects.

        Returns (list[Sentence]):
            A list with the raw Sentence objects
        """
        return self._sentences

    @property
    def ipsum_text(self) -> list[str]:
        """Return the textlines of the part with the Lorem Ipsum text.

        Returns (list[str]):
            A list with the Ipsum textlines
        """
        return self._ipsum_block

    @property
    def annotation_text(self) -> list[str]:
        """Return the textlines of the part with the annotation text.

        Returns (list[str]):
            A list with the annotation textlines
        """
        return self._annotation_block

    def __add__(self, other):
        """Concatenate, preserving metadata if possible."""
        new_text = super().__add__(str(other))
        # We can’t guess what 'other' was, so keep existing blocks
        return IpsumView(
            new_text, self._sentences, self._ipsum_block, self._annotation_block
        )

    def __radd__(self, other):
        """Concatenate when on the right-hand side."""
        new_text = str(other) + super().__str__()
        return IpsumView(
            new_text, self._sentences, self._ipsum_block, self._annotation_block
        )

    def __getitem__(self, key):
        """Support slicing — return another IpsumView for slices."""
        result = super().__getitem__(key)
        if isinstance(result, str):  # a substring, not a single character
            return IpsumView(
                result, self._sentences, self._ipsum_block, self._annotation_block
            )
        return result

    def __str__(self):
        return super().__str__()


# === END ===

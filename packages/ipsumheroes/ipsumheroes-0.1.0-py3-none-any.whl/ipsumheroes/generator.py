# src/ipsumheroes/generator.py
"""
generator.py —  The utlity functions

This module provides functionality for generating sentences and paragraphs
using the 'Loren Ipsum' language model.

It exposes two primary functions for quickly generating either a single sentence
or a paragraph composed of multiple sentences. These functions are generators
yielding objects of the type IpsumView class.
An IpsumView object behaves exactly like a string (supports concatenation,
formatting, etc.) but also keeps access to its underlying sentence-building blocks.

Text structure and formatting can be customized via parameters, including:
    - the maximum number of sections per sentence
    - the maximum number of words per section
    - the number of sentences per paragraph
    - the probability of including Luminary names in subordinate clauses
    - whether to append an annotation below each sentence or paragraph
      containing information about the referenced Luminary

Take a look at the module 'config_schema.py' for the details.

Functions:
    paragraphs(): Return an iterator over IpsumView objects, one per generated paragraph.
    paragraphs_text(): Return all generated paragraphs as a single string.
    sentences(): Return an iterator over IpsumView objects, one per generated sentence.
    sentences_text(): Return all generated sentences as a single string.
    sentence_factory(): Return a Sentence object; based on the settings of the config object.

Example 1:

    The quick method (with 6 configuration options available):

    >>> import ipsumheroes as ips

    >>> print(ips.paragraphs_text(num_paragraphs=2, luminary_probability=2)

       Beatae ut quis et asperiores necessitatibus consectetur obcaecati.
   Voluptatum reprehenderit ut aliquam unde ❮Hatshepsut❯ necessitatibus ipsam
   provident sint possimus explicabo.

       Libero ullam dignissimos placeat, ipsa
   quia quaerat odit quas totam odio laborum?  Eius ab voluptatum incidunt
   ❮Democritus❯.  Accusantium deleniti tempore eveniet esse ❮Aeschylus❯ alias

Example 2:

    For full control over formatting, with access to all available configuration
    options (over 30 in total):

    >>> import ipsumheroes as ips

    >>> cfg = ips.get_config()
    >>> cfg.num_paragpraphs = 10
    >>> cfg.with_luminaries = True
    >>> cfg.luminary_probabilty = 2
    >>> cfg.max_sentences = 10
    >>> cfg.max_sections = 3
    >>> for par in ips.paragraphs(cfg):
    ...     print(par)
    ...

       Beatae ut quis et asperiores necessitatibus consectetur obcaecati.
   Voluptatum reprehenderit ut aliquam unde ❮Hatshepsut❯ necessitatibus ipsam
   provident sint possimus explicabo.

       Libero ullam dignissimos placeat, ipsa
   quia quaerat odit quas totam odio laborum?  Eius ab voluptatum incidunt
   ❮Democritus❯.  Accusantium deleniti tempore eveniet esse ❮Aeschylus❯ alias
"""

from typing import Iterator
import random
import textwrap
from konvigius import Config
from .core import Section, Sentence, Luminary, IpsumView
from . import topic

__all__ = [
    "paragraphs",
    "paragraphs_text",
    "sentence_factory",
    "sentences",
    "sentences_text",
]

# -----------------------------------------------------------------------------
#   Function:  _normalized_tag()
# -----------------------------------------------------------------------------


def _normalized_tag(tag: str) -> str:
    if tag is not None and isinstance(tag, str):
        return tag

    return ""  # empty string


# -----------------------------------------------------------------------------
#   Function:  get_tags()
# -----------------------------------------------------------------------------


# TODO: make part of the API?
def get_tags(target: str, cfg) -> tuple[str, str]:
    start, end = None, None

    if target == "sentence":
        start = _normalized_tag(cfg.tag_sentence_start)
        end = _normalized_tag(cfg.tag_sentence_end)
    elif target == "paragraph":
        start = _normalized_tag(cfg.tag_paragraph_start)
        end = _normalized_tag(cfg.tag_paragraph_end)
    elif target == "luminary":
        start = _normalized_tag(cfg.tag_luminary_start)
        end = _normalized_tag(cfg.tag_luminary_end)
    else:
        assert False, "An unknown condition took place."

    return start, end


# -----------------------------------------------------------------------------
#   Function:  sentence_factory
# -----------------------------------------------------------------------------


def sentence_factory(cfg) -> Sentence:
    """
    Return a Sentence object; based on the settings of the config object.

    Args:
        konvigius.Config: the configuration object.

    Returns:
        Sentence: the generated Sentence instance.
    """

    # A sentence is built up of sections, each comma results in
    # a new section.
    # build array with random sections, per section an array with words.

    sections = [
        random.sample(
            list(topic.datamod.WORDS), random.randint(cfg.min_words, cfg.max_words)
        )
        for _ in range(0, random.randint(1, cfg.max_sections))
    ]

    # Replace in each section a random word with a random choosen luminary
    # name.
    # Also retrieve the data about the luminary and secure the sequence.

    luminaries: list[Luminary] = []
    if cfg.with_luminaries and cfg.luminary_probability > 0:
        for section in sections:
            if random.randint(1, 10) <= cfg.luminary_probability:
                luminary = _interpolate(section, cfg)
                luminaries.append(luminary)

    ending = random.choice(cfg.sentence_ending_punct) + cfg.spaces
    sections[-1][-1] += ending

    # return Sentence(sections, luminaries, cfg)
    return Sentence([Section(sect) for sect in sections], luminaries, cfg)


# -----------------------------------------------------------------------------
#   Function:  _interpolate()
# -----------------------------------------------------------------------------


# TODO: does now an in-place mutation AND it returns stuff. Pretty?
def _interpolate(words: list[str], cfg) -> Luminary:
    """Selects a random word from the given list and replaces it with the display text
    of a randomly chosen Luminary. This creates the impression that the text is about
    that Luminary.

    Updates the 'words' parameter in place and returns the luminary. Yes this is
    not a beautiful approach.

    Args:

    Returns:
        Luminary: The selected Luminary instance used for replacement.
    """
    stag, etag = get_tags("luminary", cfg)
    end_pos = len(words) - 1
    i = random.randint(0, end_pos)
    luminary = random.choice(cfg.topic)  # get a random luminary instance
    lum_formatted = f"{stag}{luminary.name}{etag}"
    if i == 0:
        lum_formatted = lum_formatted.lstrip()
    elif i == end_pos:
        lum_formatted = lum_formatted.rstrip()
    words[i] = lum_formatted

    return luminary


# -----------------------------------------------------------------------------
#   Function:  _indented()
# -----------------------------------------------------------------------------


def _indented(lines: list[str], first: int, next_: int) -> list[str]:
    """Return a copy of a list with indented strings."""
    indented_lines = []
    indented_lines.append(f"{first}{lines[0]}".rstrip())
    indented_lines.extend(f"{next_}{line}".rstrip() for line in lines[1:])

    return indented_lines


# -----------------------------------------------------------------------------
#   Function:  _build_annotation()
# -----------------------------------------------------------------------------


def _build_annotation(sentences: list[Sentence], cfg, space: str) -> list[str]:
    """Return a formatted text-string with the annotations.

    Collects the footnotes from the sentences.
    The function call to get_footnoot returns an already wrapped and indented text.
    Here we add some headers and make sure that the list is unique.

    Returns:
        list[str]: a list with the formatted annotations
    """
    annotation = []
    uniq = dict.fromkeys([lum for sentence in sentences for lum in sentence.luminaries])
    footnotes = [
        lum.make_footnote(
            cfg.wrap,
            cfg.anno_width,
            cfg.anno_indent_first,
            cfg.anno_indent_next,
            cfg.anno_bullet_style,
            space,
        )
        for lum in uniq.keys()
    ]

    if footnotes:
        fn_headers = [""]  # force a extra newline
        if cfg.anno_heading_1:
            fn_headers.append(f"{cfg.anno_heading_1}")
        if cfg.anno_heading_2:
            fn_headers.append(f"{cfg.anno_heading_2}")
        first = space * cfg.anno_indent_first
        next_ = first
        fn_headers = _indented(fn_headers, first=first, next_=next_)
        annotation.extend(fn_headers)
        annotation.extend(footnotes)

    return annotation


# -----------------------------------------------------------------------------
#   Function:  ipsum_factory()
# -----------------------------------------------------------------------------


def _ipsum_builder(
    sentences: list[Sentence], cfg, target: str = "paragraph"
) -> tuple[list[str], list[str]]:
    """Return a tuple 2 lists: formatted ipsum text and formatted annotation text.

    This function is the hearth of the generator engine. Based on the 'sentences' paraamter
    it formats the ipsum text and the annotation text. It sends both structures as 2
    separate lists back to the caller.

    Args:

    Returns:
        ipsum text (list[str]):
            The ipsum text is a list of sentences.

        annotation text (list[str]):
            The annotation text is a list on sentences.
    """
    if not sentences:
        raise ValueError("_ipsum_builder called with empty list sentences")

    stag, etag = get_tags("sentence", cfg)
    str_sentences = [f"{stag}{sentence}{etag}" for sentence in sentences]

    # handle indention, sentences don't use a "first" variant
    first = cfg.indent_first if target == "paragraph" else cfg.indent_next
    space = " " if cfg.no_use_nbsp_spaces else "&nbsp;"
    first = space * first
    next_ = space * cfg.indent_next

    ipsum = []

    if cfg.no_wrap:
        ipsum = _indented(str_sentences, first, next_)

    elif target in ("paragraph", "sentence"):
        # wrap it (in case of sentences the list contains only 1 item)
        raw_text = "".join(str_sentences)
        ipsum = textwrap.wrap(
            raw_text, width=cfg.width, initial_indent=first, subsequent_indent=next_
        )

    else:
        assert False, "An unknown condition took place."

    annotation = (
        _build_annotation(sentences, cfg, space)
        if (ipsum and cfg.show_annotation)
        else []
    )

    return ipsum, annotation


# -----------------------------------------------------------------------------
#   Function:  _create_view()
# -----------------------------------------------------------------------------


def _create_view(
    sentences: list[Sentence],
    ipsum: list[str],
    annotation: list[str],
    newlines: str,
    stag: str = "",
    etag: str = "",
) -> IpsumView:
    """Return a IpsumView object with the ipsum text.

    An IpsumView object behaves exactly like a string (supports concatenation,
    formatting, etc.) but also keeps access to its underlying sentence-building blocks.
    """
    lines = ipsum[:]
    lines.extend(annotation)
    text = "\n".join(lines)
    text = f"{stag}{text}{etag}{newlines}"

    return IpsumView(text, sentences, ipsum, annotation)


# -----------------------------------------------------------------------------
#   Function:  sentences()
# -----------------------------------------------------------------------------


def sentences(cfg: Config) -> Iterator[IpsumView]:
    """Return an iterator over IpsumView objects, one per generated sentence.

    Generates one sentence or a series of human-readable lorem-style sentences,
    optionally enriched with luminary references ('heroes') and annotations.

    The function yields each sentence as a string, optionally wrapped to a
    specific width and/or indented; the sentence is then packed into an
    IpsumView object.

    When `with_luminaries` is enabled, references to historical figures or other
    topics are randomly inserted into the text. If `show_annotation` is True,
    footnotes about these luminaries are appended after each sentence.

    The number of clauses per sentence, and the number of words per clause,
    can be adjusted to control sentence complexity.

    Args:
        cfg (Config): This is the Config object which contains
            all possible options. All options have a sensible default value

    Yields:
        Iterator[IpsumView]:
            A fully formatted sentence with optional luminary references and
            annotations packed in a IpsumView object.
            Note that this is a generator.
    """
    for _ in range(cfg.num_sentences):
        sentence = sentence_factory(cfg)
        ipsum, annotation = _ipsum_builder([sentence], cfg, target="sentence")
        yield _create_view([sentence], ipsum, annotation, cfg.num_newlines * "\n")


# -----------------------------------------------------------------------------
#   Function: paragraphs()
# -----------------------------------------------------------------------------


def paragraphs(cfg: Config) -> Iterator[IpsumView]:
    """Return an iterator over IpsumView objects, one per generated paragraph.

    Generates one or more formatted lorem-style paragraphs, optionally
    enriched with luminary data and annotated footnotes.

    Each paragraph consists of a random number of sentences, within the
    configured sentence range. Sentences are generated using clause and word
    constraints and may include interpolated names from a luminary dataset.

    Paragraphs are indented, optionally wrapped to a specific line width, and
    separated by line breaks. When `show_annotation` is enabled, a legend of
    all referenced luminaries is included below the paragraph.


    Args:
        cfg (Config): This is the Config object which contains
            all possible options. All options have a sensible default value

    Yields:
        Iterator[IpsumView]:
            A fully formatted paragraph with optional luminary references and
            annotations packed in a IpsumView object.
            Note that this is a generator.

    Example:
        >>> import ipsumheroes as ips
        >>> cfg = ips.get_config()
        >>> cfg.num_paragraphs = 2
        >>> cfg.with_luminaries = True
        >>> for s in ips.paragraphs(cfg):
        ...     print(s)

           Culpa nam ipsum ❮Hipparchus❯ ipsa tempora deserunt repellendus, expedita
       magnam ❮Philip II❯ obcaecati assumenda tempora quae facilis.  Quasi aperiam
       vel labore.  Possimus numquam architecto ❮Pythagoras❯, labore alias omnis
       accusamus velit doloribus voluptas dicta ullam.  Laborum ❮Pericles❯ voluptas
       rerum.

           Tenetur facere error repudiandae ❮Alexander the Great❯ veniam, excepturi
       ...
    """

    stag, etag = get_tags("paragraph", cfg)
    if stag:
        stag += "\n"
    if etag:
        etag = f"\n{etag}"

    sentence_count = lambda: random.randint(cfg.min_sentences, cfg.max_sentences)

    for i in range(0, cfg.num_paragraphs):
        sentences = [sentence_factory(cfg) for _ in range(sentence_count())]
        ipsum, annotation = _ipsum_builder(sentences, cfg)
        yield _create_view(
            sentences, ipsum, annotation, cfg.num_newlines * "\n", stag, etag
        )


# -----------------------------------------------------------------------------
#   Function: paragraphs_text()
# -----------------------------------------------------------------------------


def paragraphs_text(
    cfg: Config | None = None,
    num_paragraphs: int = 1,
    with_luminaries: bool = False,
    show_annotation: bool = False,
    luminary_probability: int = 2,
    num_newlines: int = 0,
) -> str:
    """Return all generated paragraphs as a single string.

    This is a convenience wrapper around :func:`paragraphs`. It allows generating
    text with or without an explicit configuration object. If no `cfg` is given,
    a default configuration is created automatically.

    Useful for users who prefer working with a single text string instead
    of an iterator.


    Args:
        cfg (Config, optional): A configuration object defining how text is generated.
            If omitted, a default config is created via :func:`get_config`.

        num_paragraphs (int, optional): Number of paragraphs to generate.
            Defaults to ``1``.
            Ignored if `cfg` is provided.

        with_luminaries (bool, optional): Whether to enrich text with historical
            luminary names. Defaults to ``True`` when specified.
            Ignored if `cfg` is provided.

        show_annotation (bool, optional): Whether to include annotation details
            (metadata block) below the text. Defaults to ``False``.
            Ignored if `cfg` is provided.

        luninary_probability (int, optional): Chance (0–10) of inserting a luminary reference
            into a section of each sentence.
            - ``0`` → no luminaries (same as ``with_luminaries=False``)
            - ``10`` → always include a luminary
            Intermediate values represent proportional likelihood.
            Defaults to ``2``.
            Ignored if `cfg` is provided.

        num_newlines (int, optinal): Number of blank lines between subsequent
            paragraphs.
            Defaults to ``2``.
            Ignored if `cfg` is provided.

    Returns:
        str:
            A fully formatted paragraph(s) with optional luminary references and
            annotations.

    Example:

        >>> import ipsumheroes as ips

        >>> # Quick use, with defaults, no config needed
        >>> print(ips.paragraphs_text())

           Culpa nam ipsum, expedita magnam assumenda tempora facilis.  Quasi aperiam
        vel labore.  Possimus numquam architecto , labore alias omnis accusamus velit
        doloribus voluptas dicta ullam.

        >>> # Custom call with parameters, no config needed
        >>> print(ips.sentences_text(num_paragraphs=2, with_luminaries=True))
        ...

        >>> # Full control via existing config
        >>> cfg = ips.get_config()
        >>> cfg.nu_paragraphs = 3
        >>> cfg.with_luminaries = True
        >>> cfg.max_sentences = 10
        >>> print(ips.sentences_text(cfg))

        Culpa nam ipsum ❮Hipparchus❯ ipsa tempora deserunt repellendus, expedita
        ...

        Tenetur facere error repudiandae ❮Alexander the Great❯ veniam, excepturi
        ...

        Culpa nam ipsum ❮Hipparchus❯ ipsa tempora deserunt repellendus, expedita
        ...
    """
    if cfg is None:
        from ipsumheroes import get_config  # local import to avoid circular dependency

        cfg = get_config(new=True)
        cfg.num_paragraphs = num_paragraphs
        cfg.with_luminaries = with_luminaries
        cfg.show_annotation = show_annotation
        cfg.luminary_probability = luminary_probability
        cfg.num_newlines = num_newlines

    return "".join([par + "\n" for par in paragraphs(cfg)])


# -----------------------------------------------------------------------------
#   Function: sentences_text()
# -----------------------------------------------------------------------------


def sentences_text(
    cfg: Config | None = None,
    num_sentences: int = 1,
    with_luminaries: bool = False,
    show_annotation: bool = False,
    luminary_probability: int = 2,
    num_newlines: int = 0,
) -> str:
    """Return all generated sentences as a single string.

    This is a convenience wrapper around :func:`sentences`. It allows generating
    text with or without an explicit configuration object. If no `cfg` is given,
    a default configuration is created automatically.

    Useful for users who prefer working with a single text string instead
    of an iterator.


    Args:
        cfg (Config, optional): A configuration object defining how text is generated.
            If omitted, a default config is created via :func:`get_config`.

        num_sentences (int, optional): Number of paragraphs to generate.
            Defaults to ``1``.
            Ignored if `cfg` is provided.

        with_luminaries (bool, optional): Whether to enrich text with historical
            luminary names. Defaults to ``True`` when specified.
            Ignored if `cfg` is provided.

        show_annotation (bool, optional): Whether to include annotation details
            (metadata block) below the text. Defaults to ``False``.
            Ignored if `cfg` is provided.

        luminary_probability (int, optional): Chance (0–10) of inserting a luminary reference
            into a section of each sentence.
            - ``0`` → no luminaries (same as ``with_luminaries=False``)
            - ``10`` → always include a luminary
            Intermediate values represent proportional likelihood.
            Defaults to ``2``.
            Ignored if `cfg` is provided.

        num_newlines (int, optinal): Number of blank lines between subsequent
            sentences.
            Defaults to ``2``.
            Ignored if `cfg` is provided.

    Returns:
        str:
            A fully formatted sentences(s) with optional luminary references and
            annotations.

    Example:

        >>> import ipsumheroes as ips

        >>> # Quick use, with defaults, no config needed
        >>> print(ips.sentences_text())

        Culpa nam ipsum psa tempora deserunt repellendus.

        >>> # Custom call with parameters, no config needed
        >>> print(ips.sentences_text(num_sentences=2, with_luminaries=False))
        ...

        >>> # Full control via existing config
        >>> cfg = ips.get_config()
        >>> cfg.num_sentences = 3
        >>> cfg.with_luminaries = True
        >>> print(ips.sentences_text(cfg))

        Culpa nam ipsum ❮Hipparchus❯ ipsa tempora deserunt repellendu.

        Tenetur facere error repudiandae ❮Alexander the Great❯.

        Ipsum ❮Hipparchus❯ ipsa tempora deserunt repellendus expedita.
    """
    if cfg is None:
        from ipsumheroes import get_config  # local import to avoid circular dependency

        cfg = get_config(new=True)
        cfg.num_sentences = num_sentences
        cfg.with_luminaries = with_luminaries
        cfg.show_annotation = show_annotation
        cfg.luminary_probability = luminary_probability
        cfg.num_newlines = num_newlines

    return "".join([sent + "\n" for sent in sentences(cfg)])


# === END ===

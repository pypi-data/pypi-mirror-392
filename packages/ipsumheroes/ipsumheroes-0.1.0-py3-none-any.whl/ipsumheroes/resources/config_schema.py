# src/ipsumheroes/resources/config_schema.py
"""
config_schema.py —  Defining a list with the configuration options.

This module configurates a schema (a list) with Schema objects. Each schema object
describes the metadata for a specific field from a configuration object
(a konvigius.Config object). The schema is then passed to the class method
Config.config_factory which generates a new Config object.

The order of the Schema object in this list is important because it determines the
order in which the CLI parser displays these options when the --help option is used.
"""

from .. import topic
from konvigius import Schema, Config, with_field_name
from konvigius.exceptions import ConfigRangeError


# Custom computed functions returning a value used by Schema objects


@with_field_name("spaces")
def fn_spaces(value, cfg: Config) -> str:
    #TODO: in Konigius the no-bool versions are not yet created
    space = " " if not cfg.use_nbsp_spaces else "&nbsp;"
    # space = " " if cfg.no_use_nbsp_spaces else "&nbsp;"
    return space * cfg.sentence_ending_spaces


@with_field_name("topic")
def fn_topic(value, cfg: Config) -> list[tuple[str, ...]]:
    return topic.get_topic_data(cfg.luminary_topic, cfg.luminary_lang)


# Custom validation functions that raise an error


def fn_validate_sentences(max_value, cfg: Config):
    if max_value < cfg.min_sentences:
        raise ConfigRangeError("min-sentences must be <= max-sentences")


def fn_validate_words(max_value, cfg: Config):
    if max_value < cfg.min_words:
        raise ConfigRangeError("min-words must be <= max-words")


SCHEMA = [

    # === Global options ===

    Schema("version", default=None, field_type=bool),
    Schema("read_manual", default=False, field_type=bool),
    Schema("options", default=False, field_type=bool),

    # === Generation Mode ===

    Schema("num_paragraphs|p", default=1, r_min=1, r_max=5000, field_type=int),
    Schema("num_sentences|s", default=0, r_min=0, r_max=5000, field_type=int),

    # === Paragraph / Sentence Structure ===

    Schema("num_newlines|n", default=1, r_min=0, r_max=5000, field_type=int),
    Schema("min_sentences|m", default=3, r_min=1, r_max=5000, field_type=int),
    Schema("max_sentences|x", default=8, r_min=1, r_max=5000, field_type=int,
           fn_validator=fn_validate_sentences,),
    Schema("max_sections|c", default=2, r_min=1, r_max=5, field_type=int),
    Schema("min_words", default=3, r_min=1, r_max=30, field_type=int),
    Schema("max_words", default=12, r_min=1, r_max=30, field_type=int, 
           fn_validator=fn_validate_words,),

    # === Indentation ===

    Schema("indent_first", default=7, r_min=0, r_max=100, field_type=int),
    Schema("indent_next", default=3, r_min=0, r_max=100, field_type=int),

    # === Sentence Formatting ===

    Schema("sentence_ending_punct", default="!??......", field_type=str),
    Schema("sentence_ending_spaces", default=2, r_min=1, r_max=10, field_type=int,
           fn_computed=fn_spaces,
    ),
    Schema("use_nbsp_spaces", default=False, field_type=bool),

    # === Wrapping ===

    Schema("width", default=79, r_min=5, r_max=5000, field_type=int),
    Schema("no_wrap", default=False, field_type=bool),

    # === Luminary Interpolation ===

    Schema("with_luminaries|w", default=False, field_type=bool),
    Schema("luminary_probability|y", default=3, r_min=0, r_max=10, field_type=int),
    Schema("luminary_topic|t", default="antiquity", field_type=str, 
           fn_computed=fn_topic),
    Schema("luminary_lang", default="en", field_type=str, 
           domain=("en", "nl", "du", "fr", "es"),
    ),

    # === Annotation ===

    Schema("show_annotation|a", default=False, field_type=bool),
    Schema("anno_width", default=74, r_min=5, r_max=5000, field_type=int),
    Schema("anno_indent_first", default=4, r_min=0, r_max=100, field_type=int),
    Schema("anno_indent_next", default=6, r_min=0, r_max=100, field_type=int),
    Schema("anno_heading_1", default="◆ Who They Were ◆", field_type=str),
    Schema("anno_heading_2", default="─" * 17, field_type=str),  # not just an hyphen
    Schema("anno_bullet_style", default="❯ ", field_type=str),

    # === HTML/XML Tagging ===

    Schema("tag_paragraph_start", default=None, field_type=str),
    Schema("tag_paragraph_end", default=None, field_type=str),
    Schema("tag_sentence_start", default=None, field_type=str),
    Schema("tag_sentence_end", default=None, field_type=str),
    Schema("tag_luminary_start", default=" ❮", field_type=str),
    Schema("tag_luminary_end", default="❯ ", field_type=str),
]


# === END === #

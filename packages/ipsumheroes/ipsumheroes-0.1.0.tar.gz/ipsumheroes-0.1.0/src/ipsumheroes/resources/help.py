# src/ipsumheroes/resources/help.py
"""This module contains some help texts.

The `help_options` list is used to display the help line for each option when
the CLI help option is invoked.
"""


# TODO: turn this into a jason or a toml-file
def help_options():

    options = {
        "version": "Show the version string and exit.",
        "read_manual": "Show the manual and exit.",
        "options": "Show info about options and exit.",
        "num_paragraphs": "Number of paragraphs to generate.",
        "num_sentences": "Number of sentences to generate; "
        "mutually exclusive with --num-paragraphs.",
        "num_newlines": "Number of newlines between sentences or paragraphs.",
        "min_sentences": "Minimum number of sentences per paragraph.",
        "max_sentences": "Maximum number of sentences per paragraph.",
        "max_sections": "Maximum number of sections per sentence.",
        "min_words": "Minimum number of words per sentence section.",
        "max_words": "Maximum number of words per sentence section.",
        "indent_first": "Spaces to indent the first sentence of each paragraph.",
        "indent_next": "Spaces to indent the remaining sentences of each paragraph.",
        "sentence_ending_punct": "Characters for sentence-ending punctuation.",
        "sentence_ending_spaces": "Number of spaces after each sentence.",
        "use_nbsp_spaces": "Replace formatting spaces wiht '&nbsp;' HTML-entities",
        "width": "Maximum line width before text wraps.",
        "no_wrap": "Disable text wrapping.",
        "with_luminaries": "Enable luminary name interpolation.",
        "luminary_probability": "Probability (0–10) of inserting a luminary in a sentence.",
        "luminary_topic": "Topic used for selecting luminaries.",
        "luminary_lang": "Language code for luminary data.",
        "show_annotation": "Show annotation blocks below paragraphs.",
        "anno_width": "Max line width for annotation blocks.",
        "anno_indent_first": "Indentation for the first line of annotations.",
        "anno_indent_next": "Indentation for subsequent annotation lines.",
        "anno_heading_1": "Heading for the annotation block.",
        "anno_heading_2": "Decoration below annotation heading.",
        "anno_bullet_style": "Decoration of the start of an annotation line.",
        "tag_paragraph_start": "Tag inserted at the start of each paragraph.",
        "tag_paragraph_end": "Tag inserted at the end of each paragraph.",
        "tag_sentence_start": "Tag inserted at the start of each sentence.",
        "tag_sentence_end": "Tag inserted at the end of each sentence.",
        "tag_luminary_start": "Tag inserted at the start of the name of a luminary.",
        "tag_luminary_end": "Tag inserted at the end of the name of a luminary.",
    }
    return options


# === END ===

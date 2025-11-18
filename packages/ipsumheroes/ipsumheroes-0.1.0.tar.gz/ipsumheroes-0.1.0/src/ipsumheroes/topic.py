# src/ipsumheroes/topic.py

from collections.abc import Iterable

from .core import Luminary
from .resources import topic_data as datamod

__all__ = ["get_topic_data", "get_available_topics", "add_topic"]

# -----------------------------------------------------------------------------
#   The globals
# -----------------------------------------------------------------------------

# setup of the default preferences
_interpolation_preferences = {
    "topic": "antiquity",
    "lang": "en",
    "probability": 0,
    "lbound": "",
    "rbound": "",
    "annotation": False,
}
_prefs = _interpolation_preferences  # a short alias
_current_topic_data = None  # always points to the current topic dataset

# Init topics datastore: setup single dict with all data in all languages

_datastore = {
    "antiquity": {
        "nl": datamod.ANTIQUITY_NL,
        "de": datamod.ANTIQUITY_DE,
        "fr": datamod.ANTIQUITY_FR,
        "en": datamod.ANTIQUITY_EN,
        "es": datamod.ANTIQUITY_ES,
    },
    "science": {
        "nl": datamod.SCIENCE_NL,
        "de": datamod.SCIENCE_DE,
        "fr": datamod.SCIENCE_FR,
        "en": datamod.SCIENCE_EN,
        "es": datamod.SCIENCE_ES,
    },
    "music: best selling": {"en": datamod.BEST_SELLING_BANDS},
    "music: popular": {"en": datamod.POPULAR_BANDS},
    "music: african": {"en": datamod.AFRICAN_BANDS},
}

# -----------------------------------------------------------------------------
#   Functions
# -----------------------------------------------------------------------------


def convert_to_luminaries(topic_name):

    for lang, dataset in _datastore[topic_name].items():
        converted = Luminary.instance_factory(dataset)
        _datastore[topic_name][lang] = converted


def get_topic_data(topic_name: str, lang: str = "en"):
    topic_name = topic_name.strip().lower()
    if topic_name not in _datastore.keys():
        raise ValueError(
            f"Topic '{topic_name}' is not supported. "
            + f"Available topics: {[k for k in _datastore.keys()]}"
        )
    lang = lang.strip().lower()
    if lang not in _datastore[topic_name].keys():
        raise ValueError(
            f"Language '{lang}' for topic {topic_name} is not supported."
            + f"Available languages: {[k for k in _datastore[topic_name].keys()]}"
        )
    # return the reference to the dataset of the desired topic
    return _datastore[topic_name][lang]


def reset_current_topic():
    global _current_topic_data
    _current_topic_data = _datastore[_prefs["topic"]][_prefs["lang"]]


def get_available_topics() -> list[tuple[str, tuple[str, ...]]]:
    """
    Return all available topics selectable via user preferences.

    Returns:
        list[str]:
            A list of topic names. The chosen topic determines which
           dataset is used by the interpolation function.
    """
    results = []
    for topic, dict_ in _datastore.items():
        languages = tuple([lang for lang in dict_.keys()])
        results.append(tuple([topic, languages]))
    return results


def add_topic(topic_name: str, lang: str, dataset: list[str]) -> None:
    """
    Adds a topic with its associated records.

    Although this module comes with a number of ready-to-use topics, it is
    also possible to add a custom topic with a corresponding dataset. After
    doing so, the desired topic (and language setting) must be selected via
    the preferences settings.

    A dataset is a list containing tuples. Each tuple consists of six fields,
    which can be populated as desired with values that can be converted to strings.

    List of field names:
     - name
     - role
     - note (e.g. biggest achievement)
     - region of adulthood
     - birth–death years
     - age

    Args:
        topic (str):
            The name of the topic associated with the dataset.

        lang (str):
            The language code or identifier for the dataset.

        dataset (list[tuple]):
            A list of tuples, each containing six fields. Each field should be
            convertible to a string.
    """
    topic_name = topic_name.lower().strip()
    lang = lang.lower().strip()
    if not isinstance(dataset, Iterable):
        raise TypeError("The dataset must be an  iterable object.")

    # each row must be a sequence of 6 fields
    for row in dataset:
        if not isinstance(row, Iterable):
            raise TypeError("The rows must be an iterable object.")
        if len(row) != 6:
            raise TypeError("The rows must have 6 elements.")
    topic_dict = {lang: dataset}
    _datastore[topic_name] = topic_dict
    convert_to_luminaries(topic_name)


# -----------------------------------------------------------------------------
#   The main() function
# -----------------------------------------------------------------------------

_initialized = False


def main():
    global _initialized
    if not _initialized:
        # Convert all tuples in the data containers into Luminary instances
        for topic_name in _datastore.keys():
            convert_to_luminaries(topic_name)
        # Force an init of the _topic_dataset
        reset_current_topic()
        _initialized = True


# -----------------------------------------------------------------------------
#   Init module code during first import
# -----------------------------------------------------------------------------

main()


# === END ===

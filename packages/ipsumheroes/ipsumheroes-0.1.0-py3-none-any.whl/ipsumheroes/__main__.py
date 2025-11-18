#!/bin/python
"""IpsumHeroes – where lorem ipsum meets the legends of history

Command-line tool that uses the 'ipsumheroes' library to generate lorem ipsum
text, optionally enriched with the names of great figures from antiquity,
also known as the “luminaries.”

This command-line interface provides access to all configuration options
offered by the library. For an overview of all available options, run:

$ python -m ipsumheroes --help


Example:

$ python -m ipsumheroes -p 100 --with-luminaries --max-sentences 16 > ipsum.txt

The command above generates 100 paragraphs of lorem ipsum text, sprinkled
with the names of historical luminaries. Each paragraph contains up to
16 sentences.

"""

import sys
import ipsumheroes as ips
from ipsumheroes.resources.config_schema import SCHEMA
from ipsumheroes.resources.help import help_options
from konvigius import cli_parser
from konvigius import Config
from konvigius.exceptions import ConfigError


def print_options_with_info(cfg):
    """Shows helptext with field names, current values and helptext."""
    print(cfg.inspect_vars())


def parse_cli_arguments(cfg):
    """Retrieve the choosen commandline options."""
    # Not all arguments can be created from the config, add these manually.
    cfg_kwargs = {
        "paragraphs": {"const": 1, "default": 1},
        "sentences": {"const": 1, "default": 1},
        "version": {"action": "version", "version": f"%(prog)s {ips.__VERSION__}"},
    }

    # Generate standard parse-arguments from the config object options.
    parser_args = cli_parser.create_args_from_cfg(cfg, cfg_kwargs)

    # Process the CLI arguments and update the config object accordingly.
    try:
        parser, parsed_args = cli_parser.run_parser(cfg, parser_args)
        # cli_parser.inspect_actions(parser)    DEBUG INFO
    except ConfigError as ex:
        print("Error:", ex, file=sys.__stderr__)

    return parser, parsed_args


def main():
    cfg = Config.config_factory(SCHEMA, help_map=help_options())
    parser, cli_choosen = parse_cli_arguments(cfg)

    if "read_manual" in cli_choosen:
        print("The manual can be found on github.com :")
        print("Link to manual")

    elif "options" in cli_choosen:
        print_options_with_info(cfg)

    elif "num_sentences" in cli_choosen:
        for sentence in ips.sentences(cfg=cfg):
            print(sentence)

    else:
        # --paragraphs=1 is the default choice
        for par in ips.paragraphs(cfg=cfg):
            print(par)


# --- Main section ------------------------------------------------------------

if __name__ == "__main__":

    # TOnDO: add this description
    # description = (
    #     "Generate lorem ipsum text inspired by the legends of history.\n\n"
    #     "IpsumHeroes uses the 'ipsumheroes' library to create lorem ipsum "
    #     "paragraphs optionally enriched with the names of great figures "
    #     "from antiquity, also known as the luminaries."
    # )

    main()


# === END ===

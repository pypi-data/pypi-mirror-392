# IpsumHeroes

*Where lorem ipsum meets the legends of history.*

A playful **lorem ipsum generator** that sprinkles placeholder text with the names
and quotes of **history’s luminaries and heroes**. Ideal for developers, designers,'
and writers who want their filler text to be more inspiring.

## Features

- Generate lorem ipsum with historical luminaries
- Supports English, Dutch, German, French, and Spanish
- Choose your topic from: ancient world (default), science, or music
- Add your own dataset of heroes
- Lightweight and easy to integrate

## Adjustable Parameters

- Number of sentences, paragraphs, sections, and words per section
- Sentence punctuation (`.`, `?`, `!`)
- Indentation, tags (XML/HTML), wrapping columns
- Optional value ranges for randomness

. . . and many other configuration options (see the manual).

## Usage Examples

See also the docstrings and example files in the `/examples` directory on GitHub.com

Start by importing the package under the alias `ips`:

``` python
import ipsumheroes as ips
```


### Example 1: default mode

In the default mode IpsumHeroes behaves like a normal ipsum-text generator.

``` python
text = ips.paragraphs_text(num_paragraphs=2)
print(text)

       Harum animi laboriosam distinctio voluptas quia, sunt omnis quam cumque
   voluptatibus?  Neque voluptas odit quasi commodi?  Perferendis corrupti
   assumenda fuga harum rerum suscipit ducimus voluptas fugiat porro, hic totam
   voluptate beatae delectus assumenda.  Ad repudiandae tempora laudantium.
   Hic provident veritatis aspernatur obcaecati vitae quisquam odio ullam
   minima aut?  Repellat nulla perferendis sequi fugiat consequuntur quia
   deserunt possimus recusandae quam.  Quasi nam ducimus dolore velit pariatur
   autem ipsum voluptate!

       Veritatis libero optio sit magni asperiores vero inventore.  Illum
   voluptate aliquid quae eos corrupti impedit.  Ducimus incidunt repudiandae
   perspiciatis aut facere nobis libero tenetur, rem perferendis molestias
   quae.  Ad iste repudiandae veniam excepturi amet pariatur, ducimus impedit
   alias autem adipisci praesentium placeat laudantium ipsum blanditiis.  Est
   voluptatem animi iusto maxime quasi repellat facilis sed.
```

### Example 2: with luminary enrichment

When the *luminaries switch* is on, the text is enriched with the names of ancient
luminaries. We also increase the change that a sentence will be enriched with a
luminary (scale 0 till 10).

```python
text = ips.paragraphs_text(with_luminaries=True, luminary_probability=6)
print(text)

       Culpa laudantium commodi velit incidunt porro nemo ❮Aratus❯ rerum,
   dignissimos molestias ipsa illum vero aspernatur veritatis placeat expedita.
   ❮Euclid❯ at aspernatur fugit exercitationem eius.  Magnam ❮Sophocles❯
   expedita, suscipit accusantium recusandae inventore laudantium officiis
   autem iure ❮Horace❯ voluptatem.  Placeat nihil accusantium ab fuga tempore
   ❮Xenophon❯ laboriosam dicta adipisci?  Temporibus totam sequi veritatis a
   deleniti ipsam voluptas sunt at, ducimus eaque magnam saepe.
```

To emphasize the luminaries, the default tags are adjusted so that the names are
printed in italics with an extra space around them. In this case, we need to set
additional configuration options—use the config object to do this.
See the docstrings of `paragraphs` and/or `paragraphs_text` for more details.

```python
cfg = ips.get_config()
cfg.with_luminaries = True
cfg.luminary_probability = 6
cfg.tag_luminary_start = " *"    # italic markdown support
cfg.tag_luminary_end = "* "      # italic markdown support 
text = ips.paragraphs_text(cfg)
print(text)

       *Homer*  rerum praesentium!  Dolores voluptatum quam tenetur  *Cicero*
   distinctio iusto eligendi necessitatibus ipsum, nostrum vel tempore eveniet
   quo impedit in dicta id optio hic?  Quia vitae incidunt facilis  *Julius
   Caesar*  quis saepe magni obcaecati, error possimus voluptates sapiente quos
   *Seneca the Younger*. 

cfg.tag_luminary_start = "<i>"   # italic html support
cfg.tag_luminary_end = "</i>"    # italic html support 
print(ips.paragraphs_text(cfg))

       Necessitatibus <i>Empedocles</i> dolor dicta natus odit consequatur,
   soluta et iste officiis reprehenderit voluptate modi nostrum.  Ratione
   deserunt <i>Xenophon</i>?  Eum <i>Homer</i> magnam harum iure expedita est
   reprehenderit aliquid!
```

### Example 3: adding annotation

In this example an annotations is added at the end of each paragraph. 

Here we used the convenience wrapper function without passing an explicit config
object as a parameter. If needed, you can use a config object to adjust the layout
of the annotation.

```python
text = ips.paragraphs_text(with_luminaries=True, show_annotation=True)
print(text)

       Tempore ❮Democritus❯ sint, odio sequi officia necessitatibus
   ❮Pythagoras❯ ea.  Accusantium praesentium expedita non fugiat sunt fugit
   obcaecati vitae reprehenderit asperiores.  Provident earum veniam
   ❮Eratosthenes❯ necessitatibus eos excepturi corrupti, natus iusto quidem
   maiores non ❮Imhotep❯ dolorem placeat debitis id architecto.  Provident
   autem praesentium deserunt magnam tempore inventore consectetur nulla
   explicabo consequatur.  Tenetur placeat delectus ❮Khufu❯ deleniti
   recusandae, quae sapiente quaerat corporis tempore saepe beatae perferendis
   ❮Pliny the Elder❯?  Velit ab ipsum, illum perferendis quod voluptates
   dolorem non.

    ◆ Who They Were ◆
    ─────────────────
    ❯ Democritus; Philosopher - Developed atomic theory
      Abdera, Greece; c.460–370 BCE, aged 90
    ❯ Pythagoras; Mathematician - Pythagorean theorem
      Samos/Croton; c.570–495 BCE, aged 75
    ❯ Eratosthenes; Scientist - Measured Earth's circumference
      Alexandria; c.276–194 BCE, aged 82
    ❯ Imhotep; Architect & Physician - Designed the Step Pyramid
      Egypt; c.2650–2600 BCE, aged ?
    ❯ Khufu; Pharaoh - Built Great Pyramid of Giza
      Egypt; c.2589–2566 BCE, aged ?
    ❯ Pliny the Elder; Naturalist - Wrote Natural History
      Rome; 23–79 CE, aged 56
```

## Installation

Install via pip:

```bash
pip install ipsumheroes
```

## Full Manual

For the complete manual and detailed usage examples, see the [IpsumHeroes Manual](https://github.com/rikroos/ipsumheroes/blob/master/MANUAL.md).


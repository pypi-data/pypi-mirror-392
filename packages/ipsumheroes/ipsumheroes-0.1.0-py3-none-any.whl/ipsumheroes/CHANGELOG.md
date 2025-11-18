# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]
Planned improvements for the next release (v0.1.1):

### Added
- Option flag `tag_1st_sentence` — wrap **only the first sentence** in tags.
- Option flag `tag_1st_word` — wrap **only the first word** in tags.
- Option `upper_style` — control capitalization style (`"all"`, `"1st_sentence"`, `"1st_word"`, `"luminaries"`).
- New **chapter** target type (in addition to paragraphs), with optional numbering in **decimal** or **Roman numerals**.
- Full test coverage.
- A manual, for now, refer to docstrings and example files.

### Planned
- Support configuration not only via the internal `Schema` class, but also through a **TOML** or **JSON** schema definition.
- Possibly introduce a redesigned **tagging configuration model** to improve flexibility.

### Example usage
```bash
$ ipsumheroes --tag-sentence-start "<i>" --tag-sentence-end "</i>" --tag-1st-sentence --upper-style 1st_word
```

---

## [0.1.0] - 2025-11-13
- First public release of IpsumHeroes — stable and feature complete for initial use.

### Added
- Package module (`__init__.py`), defining the public API.
- `generator.py` responsible for lorem ipsum text generation.
- Resource datasets for luminary data (Ancient World, Science, Music).
- `/examples` directory with demonstration files showing library usage.
- Unit tests with >90 % coverage.
- Tooling and linting setup using `black`, `ruff`, and `pyright`.
- Placeholder `MANUAL.md` document.
- Runtime configuration implemented via the `konvigius` package.
- Realized test coverage 

### Fixed
- N/A

### Changed
- N/A

### Notes
- A detailed manual is planned for the next release (for now, refer to docstrings and example files).

---

## [0.0.1] - 2025-11-01
Initial internal release.

### Added
- Initial `IpsumHeroes` library package structure.

### Fixed
- N/A (first release)

### Changed
- N/A (first release)


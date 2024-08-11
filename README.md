# :bookmark_tabs: Post-It

[![checks](https://github.com/brennenho/post-it/actions/workflows/checks.yml/badge.svg)](https://github.com/brennenho/post-it/actions/workflows/checks.yml)

A robust, extensible Python data tagging framework for dynamic processing and intelligent filtering of pretraining corpora for AI models.

## Getting Started

Install from [PyPi](https://pypi.org/project/postit/):
```
pip install postit
```

To learn more about using Post-It, please visit the [documentation](https://github.com/brennenho/post-it/tree/main/docs).

## Why Data Tagging?

Data is the backbone of machine learning. With a vast variety of companies developing ML models, processing and filtering data to create high-quality datasets is extremely important.

The popularity of **continued pretraining** (performing pretraining on existing LLMs for domain-adaptation) makes tools like Post-It increasingly important.

In addition, tagging data instead of directly filtering it provides flexibility. It is easy to test the impact of removing different types of data on the final pretraining corpus, enabling quick iteration.

## Why Post-It?
- **Extensible:** Designed for easy adaptation into any number of data processing workflows.
- **Fast:** Built-in parallization to process large datasets.
- **Flexible:** Supports local and remote cloud storage.
- **Capable:** Packaged with a variety of popular taggers, ready to use out of the box.

## Contributing

- Clone this repo
- Install [Poetry](https://python-poetry.org/docs/)
- Activate Poetry: `poetry shell`
- Install dependencies: `poetry install`
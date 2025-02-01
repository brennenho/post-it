
![Banner](https://raw.githubusercontent.com/brennenho/post-it/refs/heads/main/docs/assets/banner.png)

# Post-It
[![license](https://img.shields.io/github/license/brennenho/post-it?style=flat-square)](https://github.com/brennenho/post-it/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/postit.svg?style=flat-square&label=PyPI)](https://pypi.org/project/postit/)
[![checks](https://img.shields.io/github/actions/workflow/status/brennenho/post-it/checks.yml?branch=main&style=flat-square&label=checks)](https://github.com/brennenho/post-it/actions/workflows/checks.yml)

A robust, extensible Python data tagging framework for dynamic processing and intelligent filtering of pretraining corpora for AI models.

## Getting Started

Install from [PyPi](https://pypi.org/project/postit/):
```
pip install postit
```

To learn more about using Post-It, please visit the [documentation](https://github.com/brennenho/post-it/tree/main/docs).

## Why Data Tagging?

![Diagram](https://raw.githubusercontent.com/brennenho/post-it/refs/heads/main/docs/assets/diagram.png)

Datasets form the backbone of modern machine learning. A high-quality dataset is vital to successfully train an AI model. Data tagging is the process of labeling raw data based on the content of the data and related metadata.

The labels created by data tagging can then be used to filter out low-quality data to create a final training corpus. Efficient data tagging is becoming increasingly important with the growing popularity of **continued pretraining** (pretraining an existing LLM, often to adapt the model to a specific domain).

Without data tagging, creating a high-quality dataset involves directly filtering out poor data. This makes iteration and testing of different types of filters difficult and inefficient.

## Why Post-It?
- **Extensible:** Designed for easy adaptation into any number of data processing workflows.
- **Fast:** Built-in parallization enables efficient processing of large datasets.
- **Flexible:** Supports local and remote cloud storage.
- **Capable:** Packaged with a variety of popular taggers, ready to use out of the box.

## Contributing

See [contributing](https://github.com/brennenho/post-it/blob/main/CONTRIBUTING.md).
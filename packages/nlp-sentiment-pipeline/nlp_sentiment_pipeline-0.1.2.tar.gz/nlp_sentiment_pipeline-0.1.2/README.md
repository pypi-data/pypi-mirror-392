# NLP Sentiment Analysis Pipeline

A comprehensive, modular pipeline for sentiment analysis using deep learning models. This package provides tools for data extraction, preprocessing, model training, and evaluation.

## Features

- **Data Preparation**: Extract and preprocess text data for sentiment analysis
- **Modeling**: Baseline models with TF-IDF vectorization and neural networks
- **Evaluation**: Comprehensive model evaluation utilities

## Installation

### From PyPI (once published)

```bash
pip install nlp-sentiment-pipeline
```

### From Source

```bash
git clone https://github.com/FranzCastillo/NLP-Tweets-Sentiment-Analysis-DL-Models
cd NLP-Tweets-Sentiment-Analysis-DL-Models/pipeline
pip install -e .
```

### For Development

```bash
pip install -e ".[dev]"
```

## Usage

### As a Python Package

```python
from pipeline.data_preparation import DataExtractor, TextPreprocessor, DataSplitter
from pipeline.modeling import BaselineModel, TfidfVectorizerWrapper
from pipeline.evaluation import ModelEvaluator

# Extract data
extractor = DataExtractor(split="train")
df = extractor.extract()

# Preprocess text
preprocessor = TextPreprocessor(remove_stopwords=True)
df['clean_text'] = df['text'].apply(preprocessor.preprocess)

# Train model
model = BaselineModel()
# ... training code ...

# Evaluate
evaluator = ModelEvaluator(model, X_test, y_test)
results = evaluator.evaluate()
```

### As a Command-Line Tool

```bash
nlp-sentiment-pipeline
```

## Package Structure

```
pipeline/
├── __init__.py
├── main.py
├── data_preparation/      # Data extraction and preprocessing
│   ├── __init__.py
│   ├── extraction.py
│   ├── preprocessing.py
│   └── data_splitter.py
├── modeling/              # Model definitions and utilities
│   ├── __init__.py
│   ├── baseline.py
│   ├── vectorizer.py
│   └── model_evaluator.py
└── evaluation/            # Evaluation utilities
    ├── __init__.py
    ├── evaluator.py
    └── model_evaluator.py
```

## Subpackages

### data_preparation

Tools for data extraction and preprocessing:
- `DataExtractor`: Extract datasets from various sources
- `TextPreprocessor`: Clean and preprocess text data
- `DataSplitter`: Split data into train/validation/test sets

### modeling

Model implementations and utilities:
- `BaselineModel`: Baseline neural network model
- `TfidfVectorizerWrapper`: TF-IDF vectorization wrapper
- Various deep learning models

### evaluation

Model evaluation tools:
- `ModelEvaluator`: Comprehensive model evaluation
- `evaluate_model`: Quick evaluation function
- `print_evaluation_results`: Pretty-print evaluation metrics

## Requirements

- Python >= 3.8
- TensorFlow >= 2.15.0
- pandas >= 2.3.1
- scikit-learn >= 1.5.2
- nltk >= 3.9.1
- spacy >= 3.8.7

See `requirements.txt` for a complete list of dependencies.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black pipeline/
```

### Type Checking

```bash
mypy pipeline/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Authors

Francisco Castillo - cas21562@uvg.edu.gt

## Changelog

### 0.1.2 (2025-11-15)
- Second test release for PyPI publishing
- CI/CD pipeline testing

### 0.1.1 (2025-11-15)
- Test release for CI/CD pipeline
- Updated GitHub Actions workflows

### 0.1.0 (2025-11-14)
- Initial release
- Data preparation subpackage
- Modeling subpackage
- Evaluation subpackage

# TextAnalyser

A modular PDF text analysis and extraction system that processes PDF documents to extract structured content, headings, and document hierarchy.

## Features

- 📑 PDF text extraction with structure preservation
- 🔍 Intelligent heading detection
- 📊 Document hierarchy analysis
- 🚀 Multi-threaded processing
- 📈 Performance monitoring
- 🔧 Customizable configuration

## Prerequisites

- Docker Desktop
- Python 3.11 (if running locally)
- Input PDF files to process

## Quick Start with Docker

1. **Build the Docker image:**
   ```bash
   docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
   ```

2. **Prepare your files:**
   - Create an `input` directory in your project folder
   - Place PDF files you want to analyze in the `input` directory (PDF files should process within 10 seconds for 50 pages)
   - Create an `output` directory for results

3. **Run the container:**
   ```bash
   docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolutionname:somerandomidentifier
   ```

Note: The container will:
- Process all PDFs from `/app/input` directory automatically
- Generate `filename.json` in `/app/output` for each `filename.pdf`
- Complete processing within 10 seconds for a 50-page document
- Run in isolated network mode for security
- Clean up automatically after execution (--rm flag)

## Project Structure

```
TextAnalyser/
├── input/                  # Place input PDF files here
├── output/                 # Processed results appear here
├── analyzers/             # Document analysis components
├── extractors/            # PDF extraction modules
├── enhancers/            # Output enhancement modules
├── config/               # Configuration files
└── main_modular.py      # Main entry point
```

## Configuration

The system can be customized via the configuration in `main_modular.py`:

```python
custom_config = {
    'extraction': {
        'max_workers': 3,
        'font_thresholds': {
            'min_heading_size': 10.0,
            'large_font_threshold': 14.0
        }
    }
}
```

## Output Format

The system generates JSON output files containing:
- Document title
- Extracted headings with hierarchy
- Page numbers
- Document structure

## Local Development

If you prefer to run without Docker:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the analyzer:
   ```bash
   python main_modular.py
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

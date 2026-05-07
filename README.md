# **Tweet Audit Application** 

## Overview
A robust Python application designed for automated X (former twitter) post moderation, leveraging Google's Gemini AI to analyze tweets against predefined criteria. It my X posts, identifies problematic content, and prepares a report for review.

## Features
*   **AI-Powered Content Analysis**: Utilizes Google Gemini to intelligently audit tweet content for adherence to moderation policies.
*   **Modular Architecture**: Built with a clean, layered design that promotes maintainability, testability, and scalability across different components.
*   **Batch Processing with Checkpointing**: Efficiently processes large volumes of tweets in batches, with a checkpointing mechanism for resilience and graceful recovery from interruptions.
*   **Robust Data Validation**: Employs `Pydantic` schemas to ensure data integrity and type safety throughout the parsing and analysis pipeline.
*   **Comprehensive Logging**: Integrates `rich` for enhanced, human-readable console output and detailed file logging, making runtime behavior easily observable.
*   **Flexible Data Handling**: Supports parsing tweet data from JSON files and outputs structured analysis results to CSV format.

## Getting Started

Follow these steps to set up and run the Tweet Audit Application locally.

### Installation

1.  **Clone the Repository**:
    Begin by cloning the project repository to your local machine:
    ```bash
    git clone https://github.com/ojogu/twee-audit.git
    cd twee-audit
    ```

2.  **Set up Python Environment**:
    This project requires Python 3.12 or newer. It's recommended to use a virtual environment.
    *   🐍 Create a virtual environment:
        ```bash
        python -m venv venv
        ```
    *   ⚙️ Activate the virtual environment:
        *   On macOS/Linux:
            ```bash
            source venv/bin/activate
            ```
        *   On Windows:
            ```bash
            .\venv\Scripts\activate
            ```

3.  **Install Dependencies**:
    Install all required Python packages using `uv`:
    ```bash
    uv sync
    ```
    this would update from the pyproject.toml

### Environment Variables

The application requires specific environment variables for AI model access. Create a `.env` file in the root directory of the project (next to `pyproject.toml` and `src/`) and populate it with your Google API Key and desired model name.

**Example `.env` file:**
```
GOOGLE_API_KEY="your_google_gemini_api_key_here"
MODEL_NAME="gemini-pro" # Or another suitable Gemini model
```

## Usage

The Tweet Audit Application follows a multi-step process: data extraction, initial CSV writing, and then AI-driven analysis.

1.  **Prepare Input Data**:
    Place your tweet archive JSON file (e.g., `tweets.json`) inside the `data/` directory. The expected structure for each tweet entry in the JSON file is:
    ```json
    [
      {
        "tweet": {
          "id_str": "1234567890",
          "full_text": "This is the content of the tweet."
        }
      },
      {
        "tweet": {
          "id_str": "0987654321",
          "full_text": "Another tweet's content."
        }
      }
    ]
    ```
    If the `data/` directory or `tweets.json` file doesn't exist, they will be created automatically, but you'll need to populate `tweets.json` with your data.

2.  **Initial Data Extraction and Formatting (First Run)**:
    The `src/main.py` script contains commented-out lines for initial data extraction and CSV writing. For the first run, you will need to uncomment these lines to process your `tweets.json` and create the `data/extracted_tweets.csv` file.

    Modify `src/main.py` to look like this (uncommenting the first two lines):
    ```python
    # ... (imports and Application class definition)
                
    if __name__ == "__main__":
        app = Application()
        data = app.extract_tweet_from_json()
        app.write_tweets_from_json_to_csv(data)
        # app.read_processed_csv_waiting_for_analysis() # This line is optional for debugging
        app.analyze_tweets()
    ```
    Run this once to convert your `tweets.json` into a CSV format suitable for analysis:
    ```bash
    python src/main.py
    ```
    This will create `data/extracted_tweets.csv` containing `id` and `content` columns.

3.  **Perform AI Analysis**:
    After the initial data extraction, you can revert `src/main.py` to its original state (commenting out the first two lines again if you only want to run analysis). The `analyze_tweets` function will read from `data/extracted_tweets.csv`, send content to the configured Google Gemini model, and write problematic tweet URLs to `data/analyzed_tweets.csv`.

    Run the analysis:
    ```bash
    python src/main.py
    ```
    The `data/analyzed_tweets.csv` will then contain a list of `tweet_url` and a `deleted` boolean indicating if the tweet should be removed based on the AI audit.

## Technologies Used

| Technology         | Description                                                              |
| :----------------- | :----------------------------------------------------------------------- |
| Python             | Primary programming language.                                            |
| Google Gemini API  | AI model integration for content analysis.                               |
| Pydantic           | Data validation and settings management.                                 |
| Rich               | Beautiful terminal rendering and advanced logging.                       |
| `pathlib`          | Object-oriented filesystem paths.                                        |
| `csv`              | CSV file reading and writing.                                            |
| `json`             | JSON data parsing.                                                       |
| `logging`          | Standard library for flexible event logging.                             |
| `re`               | Regular expression operations for string manipulation.                   |

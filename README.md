
# Zomato RAG Project

A Retrieval-Augmented Generation (RAG) system for restaurant menu information, built as part of the Zomato Gen AI Internship Assignment.

## Project Overview

This project implements an end-to-end Generative AI solution combining web scraping with a RAG-based chatbot. The system allows users to ask natural language questions about restaurants and receive accurate, contextual responses based on scraped restaurant menu data.

## Features

- **Web Scraping**: Collects restaurant data including menu items, prices, and dietary information.
- **Vector Search**: Enables semantic search across restaurant menu information.
- **Conversation Memory**: Maintains context across multiple queries in a conversation.
- **Interactive Interface**: Simple Gradio UI for natural interaction with the system.

## Project Structure

```
Zomato-Project/
├── __pycache__/            # Python cache files
├── data/                   # Restaurant menu datasets
├── scrape/                 # Web scraping modules
│   ├── menu.py             # Menu data scraping functionality
│   └── zommy.py            # Zomato-specific scraping utilities
├── .env                    # Environment variables (not tracked by git)
├── .gitignore              # Git exclusion patterns
├── app.py                  # Main application entry point
├── data_loading.ipynb      # Data processing notebook
├── requirements.txt        # Project dependencies
└── utils.py                # Utility functions
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/akshatshaw/Zomato_RAG.git
   cd Zomato_RAG
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up MongoDB:
   - Install MongoDB if not already installed.
   - Create a `.env` file with your MongoDB connection details.

## Usage

### 1. Data Collection

To scrape restaurant data (only needed if starting from scratch):

```bash
python scrape/menu.py
```

### 2. Launch the Application

Start the chatbot interface:

```bash
python app.py
```

The Gradio interface will launch in your default web browser, allowing you to interact with the system.

### 3. Example Queries

- "What vegetarian items are available at Bombay Bistro?"
- "How much do the desserts cost at Taj Restaurant?"
- "Are there any gluten-free options at Spice Garden?"
- "Compare the pizza options between Roma's and Napoli's"

## Technical Details

- **Embedding Model**: `nomic-ai/nomic-embed-text-v1`
- **LLM Integration**: HuggingFace models via API
- **Database**: MongoDB with vector search capabilities
- **UI Framework**: Gradio

## Future Improvements

- Enhanced multi-modal support for menu images
- Integration with real-time Zomato API
- Expanded language support
- User preference modeling for personalized recommendations

## License

MIT

## Acknowledgments

This project was created for the Zomato Gen AI Internship Assignment. Special thanks to the Zomato team for the opportunity.

# Telegram AI Chatbot

This is a Telegram chatbot powered by AI, which includes features such as AI chat, web search, image analysis, and sentiment analysis. The bot is built using Python, MongoDB, and the Gemini API.

## Features
- **AI Chat**: Chat with AI using Google's Gemini model.
- **Web Search**: Perform Google searches and get summarized results.
- **Image Analysis**: Upload images, and the bot will describe them using AI.
- **Sentiment Analysis**: Analyze the sentiment of a given text.

## Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud instance)
- A Telegram Bot Token
- Google Gemini API Key
- Google Custom Search Engine (CSE) API Key

### Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/hrishabh1103/telegram_ai_bot.git
   cd telegram_ai_bot
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Environment Variables
Create a `.env` file in the project directory and add:
```ini
TOKEN=<your_telegram_bot_token>
MONGO_URI=<your_mongo_db_uri>
GEMINI_API_KEY=<your_gemini_api_key>
GOOGLE_API_KEY=<your_google_api_key>
GOOGLE_CSE_ID=<your_google_cse_id>
```

### Running the Bot Locally
```sh
python bot.py
```

## Usage
- Start the bot in Telegram by sending `/start`.
- Select a feature from the menu.
- Send text or images for analysis.

## License
This project is licensed under the MIT License.

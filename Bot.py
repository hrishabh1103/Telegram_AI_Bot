import os
import logging
import requests
import pymongo
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import io
import google.generativeai as genai
from PIL import Image
from textblob import TextBlob  # Sentiment analysis

# Load environment variables
TOKEN = "7750761932:AAGmCl3VtKm0CtIjx1wRYqjgqrXQ0tUl_rU"
MONGO_URI = "mongodb://localhost:27017"
GOOGLE_API_KEY = "AIzaSyDbXZ7LlDkplrYzP_0eyYA-9EICSf32aX4"
GOOGLE_CSE_ID = "64bb9f28e5e324819"
GEMINI_API_KEY = "AIzaSyAxXSuxmcb1mMWYCDm54ZPWZIocyBPYyfE"

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize MongoDB client
client = pymongo.MongoClient(MONGO_URI)
db = client["telegram_bot"]
users_collection = db["users"]
chat_history_collection = db["chat_history"]
file_metadata_collection = db["file_metadata"]

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Bot states
SELECT_FEATURE, CHAT_AI, WEB_SEARCH, IMAGE_ANALYSIS = range(4)

async def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat_id
    existing_user = users_collection.find_one({"chat_id": chat_id})
    
    if not existing_user:
        users_collection.insert_one({"first_name": user.first_name, "username": user.username, "chat_id": chat_id})
        await update.message.reply_text("Welcome! Please share your phone number using the contact button.")
    
    return await show_menu(update, context)

async def show_menu(update: Update, context: CallbackContext) -> int:
    keyboard = [["AI Chat", "Web Search"], ["Image Analysis", "Sentiment Analysis"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Select a feature:", reply_markup=reply_markup)
    return SELECT_FEATURE

async def select_feature(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    chat_id = update.message.chat_id
    
    if text in ["AI Chat", "Web Search", "Image Analysis", "Sentiment Analysis"]:
        context.user_data["selected_feature"] = text
        await update.message.reply_text(f"You selected {text}. Send your input.")
        return CHAT_AI if text == "AI Chat" else WEB_SEARCH if text == "Web Search" else IMAGE_ANALYSIS if text == "Image Analysis" else CHAT_AI
    else:
        await update.message.reply_text("Invalid choice. Please select from the menu.")
        return SELECT_FEATURE

async def handle_message(update: Update, context: CallbackContext) -> int:
    user_message = update.message.text
    selected_feature = context.user_data.get("selected_feature")
    
    if selected_feature == "AI Chat":
        response = model.generate_content(user_message)
        ai_response = response.text if hasattr(response, "text") else "I couldn't process your request."
        await update.message.reply_text(ai_response)
    elif selected_feature == "Web Search":
        url = f"https://www.googleapis.com/customsearch/v1?q={user_message}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
        response = requests.get(url).json()
        if "items" in response:
            results = "\n".join([f"{item['title']}: {item['link']}" for item in response["items"][:3]])
            await update.message.reply_text(f"Top search results:\n{results}")
        else:
            await update.message.reply_text("No results found.")
    elif selected_feature == "Sentiment Analysis":
        sentiment = TextBlob(user_message).sentiment.polarity
        if sentiment > 0:
            mood = "Positive 😊"
        elif sentiment < 0:
            mood = "Negative 😞"
        else:
            mood = "Neutral 😐"
        await update.message.reply_text(f"Sentiment Analysis Result: {mood}")
    elif selected_feature == "Image Analysis":
        await update.message.reply_text("Please send an image for analysis.")
    else:
        return await show_menu(update, context)
    
    return SELECT_FEATURE

async def analyze_image(update: Update, context: CallbackContext) -> int:
    photo = update.message.photo[-1] if update.message.photo else None
    if photo:
        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()
        
        try:
            image_data = Image.open(io.BytesIO(file_bytes))  # Convert bytes to PIL image
            response = model.generate_content(["Describe this image:", image_data])
            description = response.text if hasattr(response, "text") else "No description available."
            
            metadata = {"filename": file.file_path, "description": description}
            file_metadata_collection.insert_one(metadata)
            
            await update.message.reply_text(f"Image Analysis: {description}")
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            await update.message.reply_text(f"Error processing image. Please try again.\n\nDebug Info: {str(e)}")
    else:
        await update.message.reply_text("Please send an image.")
    
    return SELECT_FEATURE

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_FEATURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_feature)],
            CHAT_AI: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            WEB_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            IMAGE_ANALYSIS: [MessageHandler(filters.PHOTO, analyze_image)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()

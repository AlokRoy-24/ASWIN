from typing import Final
from telegram import Update, File
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pipeline import chat_pipeline, transcribe_audio  # Import pipeline functions
import os
from gtts import gTTS  
from googletrans import Translator
from dotenv import load_dotenv

load_dotenv()
# Constants
TOKEN: Final = os.getenv('TOKEN')
BOT_USERNAME: Final = '@AshwinYojnabot'
TEMP_AUDIO_DIR: Final = 'temp_audio'

# Ensure temporary audio directory exists
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

translator = Translator()

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks for chatting with me! I can respond to your queries with text or voice!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Send me a message or a voice note, and I will respond in the same format!')

# Generate voice response
def generate_voice_response(text: str, language: str) -> str:
    audio_file_path = os.path.join(TEMP_AUDIO_DIR, "response.ogg")
    tts = gTTS(text=text, lang=language)
    tts.save(audio_file_path)
    return audio_file_path

# Translate text
async def translate_text(text: str, dest_language: str) -> str:
    try:
        async with Translator() as translator:
            result = await translator.translate(text, dest='hi')
            return result.text
        
    except Exception as e:
        print(f"Error translating text: {e}")
        return text  

# Voice message handler
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = None
    voice_response_path = None
    try:
        # Download the voice file
        file: File = await update.message.voice.get_file()
        file_path = os.path.join(TEMP_AUDIO_DIR, f"{file.file_id}.ogg")
        await file.download_to_drive(file_path)

        print(f"Downloaded voice note to {file_path}")

        # Transcribe the voice file
        transcription = transcribe_audio(file_path)
        print(f"Transcription: {transcription}")

        # Generate response text using the pipeline
        response_text = chat_pipeline(transcription)
        print("Bot Response (Before Translation):", response_text)

        # Detect language from transcription (default to 'hi' if detection fails)
        detected_language = 'hi'

        # Translate the response if necessary
        translated_response = await translate_text(response_text, dest_language=detected_language)
        print("Bot Response (Translated):", translated_response)

        # Generate voice response
        voice_response_path = generate_voice_response(translated_response, detected_language)

        # Send the voice response back to the user
        with open(voice_response_path, "rb") as voice_response_file:
            await update.message.reply_text(translated_response)
            await update.message.reply_voice(voice_response_file)

    except Exception as e:
        print(f"Error handling voice message: {e}")
        voice_response_path = generate_voice_response("मुझे आपकी आवाज़ नोट को संसाधित करने में समस्या हो रही है। कृपया फिर से प्रयास करें।", "hi")
        with open(voice_response_path, "rb") as voice_response_file:
            # await update.message.reply_text(response_text)
            await update.message.reply_voice(voice_response_file)

    finally:
        # Cleanup temporary files
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if voice_response_path and os.path.exists(voice_response_path):
            os.remove(voice_response_path)

# Text message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    print(f"User ({update.message.chat.id}): \"{text}\"")

    try:
        response_text = chat_pipeline(text)
        print("Bot:", response_text)
        await update.message.reply_text(response_text)
    except Exception as e:
        print(f"Error handling text message: {e}")
        await update.message.reply_text("मुझे आपके संदेश को संसाधित करने में समस्या हो रही है। कृपया फिर से प्रयास करें।")

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

# Main function
if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    # Errors
    app.add_error_handler(error)

    # Poll the bot
    print('Polling...')
    app.run_polling(poll_interval=3)

# Multimodal Chatbot with Groq API and Telegram Bot Integration

This project is a multimodal chatbot powered by the Groq API, enabling conversational AI that supports both text and voice inputs. The bot is deployed on Telegram and can respond to user queries in text or voice format, leveraging retrieval-augmented generation (RAG) for context-based answers.

---

## Features

- **Text and Voice Input Support**: 
  Users can send text messages or voice notes to the bot.
  
- **Contextual Responses with RAG**: 
  Queries are answered using a combination of document retrieval and Groq's LLM.

- **Language Translation**: 
  Bot responses are translated to Hindi or other languages as required.

- **Voice Responses**: 
  The bot generates voice responses for text and voice queries using Google Text-to-Speech (gTTS).

---

## Tech Stack

- **Groq API**: For LLM and Whisper (speech-to-text) functionalities.
- **LangChain**: Framework for conversational AI and RAG setup.
- **ChromaDB**: Vector store for storing and retrieving document embeddings.
- **Google Translate**: For language translation.
- **gTTS**: Converts text responses to audio.
- **Python-Telegram-Bot**: For Telegram integration.

---

## Prerequisites

1. Python 3.8 or above
2. Telegram Bot API Token (get it from [BotFather](https://core.telegram.org/bots#botfather))
3. Groq API Key (register at [Groq API](https://groq.com/))

import os
import anthropic
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# Tes clés (Railway les lira automatiquement)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN manquant !")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY manquant !")

# Client Claude
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Historique des conversations par utilisateur
conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bonjour ! Je suis un assistant IA propulsé par Claude.\n"
        "Envoie-moi n'importe quel message et je te répondrai !"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    # Initialiser l'historique si nouveau user
    if user_id not in conversations:
        conversations[user_id] = []

    # Ajouter le message de l'utilisateur
    conversations[user_id].append({
        "role": "user",
        "content": user_message
    })

    # Garder seulement les 20 derniers messages (mémoire)
    if len(conversations[user_id]) > 20:
        conversations[user_id] = conversations[user_id][-20:]

    try:
        # Appel à Claude
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system="Tu es un assistant utile et sympathique. Réponds toujours dans la langue de l'utilisateur.",
            messages=conversations[user_id]
        )

        reply = response.content[0].text

        # Sauvegarder la réponse dans l'historique
        conversations[user_id].append({
            "role": "assistant",
            "content": reply
        })

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"❌ Erreur : {str(e)}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot démarré !")
    app.run_polling()

if __name__ == "__main__":
    main()

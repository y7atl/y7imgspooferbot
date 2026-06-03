#!/usr/bin/env python3
"""
Telegram Image Cleaner Bot
- Strips all EXIF/metadata from photos
- Applies subtle brightness/contrast tweak to change file fingerprint
- Resaves as clean JPEG
"""

import os
import io
import logging
from PIL import Image, ImageEnhance
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN", "8979975887:AAH5GVIWathboJPdYoKs_Hdsql-X0qu1tjs")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Envoie-moi une photo et je te la retourne :\n"
        "✅ Sans métadonnées (GPS, appareil, date...)\n"
        "✅ Légèrement retouchée (nouvelle signature numérique)\n\n"
        "Ta vie privée est protégée 🔒"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Nettoyage en cours...")

    # Télécharger la photo en meilleure qualité
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    buf_in = io.BytesIO()
    await file.download_to_memory(buf_in)
    buf_in.seek(0)

    # Ouvrir avec Pillow (supprime automatiquement les métadonnées EXIF)
    img = Image.open(buf_in).convert("RGB")

    # Légère retouche pour changer la signature numérique du fichier
    img = ImageEnhance.Brightness(img).enhance(1.08)
    img = ImageEnhance.Contrast(img).enhance(0.93)
    img = ImageEnhance.Color(img).enhance(1.05)

    # Sauvegarder SANS métadonnées (pas de paramètre exif= → aucune donnée)
    buf_out = io.BytesIO()
    img.save(buf_out, format="JPEG", quality=92, optimize=True)
    buf_out.seek(0)

    await msg.delete()
    await update.message.reply_photo(
        photo=buf_out,
        caption="✅ Photo nettoyée — métadonnées supprimées"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère aussi les images envoyées comme fichier (pas compressées)"""
    doc = update.message.document
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        await update.message.reply_text("❌ Envoie une image (JPG, PNG, WEBP...)")
        return

    msg = await update.message.reply_text("⏳ Nettoyage en cours...")

    file = await context.bot.get_file(doc.file_id)
    buf_in = io.BytesIO()
    await file.download_to_memory(buf_in)
    buf_in.seek(0)

    img = Image.open(buf_in).convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(1.02)
    img = ImageEnhance.Contrast(img).enhance(0.99)

    buf_out = io.BytesIO()
    img.save(buf_out, format="JPEG", quality=92, optimize=True)
    buf_out.seek(0)

    await msg.delete()
    await update.message.reply_photo(
        photo=buf_out,
        caption="✅ Photo nettoyée — métadonnées supprimées"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    print("Bot démarré ✅")
    app.run_polling()

if __name__ == "__main__":
    main()

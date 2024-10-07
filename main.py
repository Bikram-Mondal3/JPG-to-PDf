import os
import telebot
import time
from PIL import Image
from reportlab.pdfgen import canvas

BOT_TOKEN = os.environ.get("Bot-token") 

bot = telebot.TeleBot(BOT_TOKEN)

# Store photos temporarily
user_photos = {}

def convert_images_to_pdf(image_files, output_pdf):
    c = canvas.Canvas(output_pdf)
    for image_file in image_files:
        img = Image.open(image_file)
        width, height = img.size
        c.setPageSize((width, height))
        c.drawImage(image_file, 0, 0, width, height)
        c.showPage()
    c.save()

# Message handler that handles incoming /start, /hello, and /hi commands.
@bot.message_handler(commands=['start', 'hello', 'hi'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Nice to meet you. Is there anything I can assist you?")


@bot.message_handler(commands=['done'])
def handle_done(message):
    user_id = message.from_user.id
    if user_id not in user_photos or not user_photos[user_id]:
        bot.reply_to(message, "No photos to process.")
        return

    output_pdf = 'output.pdf'
    convert_images_to_pdf(user_photos[user_id], output_pdf)
    
    with open(output_pdf, 'rb') as pdf_file:
        bot.send_document(message.chat.id, pdf_file)
    
    # Clean up temporary files
    for file_path in user_photos[user_id]:
        os.remove(file_path)
    os.remove(output_pdf)
    
    # Clear the photos for the user
    user_photos[user_id] = []
    bot.reply_to(message, "PDF created and sent!")

    
# Handling random Text Messages    
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.reply_to(message, "I received your message: " + message.text)

# Handling photos
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id

    # Initialize user photos list if not already
    if user_id not in user_photos:
        user_photos[user_id] = []

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Save the image to a temporary file
    temp_image = f'temp_image_{len(user_photos[user_id])}.jpg'
    with open(temp_image, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    # Add the temp image file path to the list
    user_photos[user_id].append(temp_image)
    
    bot.reply_to(message, "Photo received. Send more photos or type /done when finished.")


# Add the following to the end of your file to launch the bot
bot.infinity_polling()

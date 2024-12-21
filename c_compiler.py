import os
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters

# Directory to store uploaded files temporarily
UPLOAD_FOLDER = "./uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the directory if it doesn't exist

# /start command handler
async def start(update: Update, context: CallbackContext) -> None:
    welcome_message = (
        "*Welcome to C to Binary Compiler Bot!* 🎉\n\n"
        "👨‍💻 Send me a C file with the `.c` extension, and I'll compile it into a binary for you. 💻⚙️\n\n"
        "Once uploaded, I'll compile it and send you the compiled binary right here in the chat. 📥🔧\n\n"
        "Let's get started! Upload your file and let me handle the rest! 🚀"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

# Handle uploaded C files
async def handle_c_file(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    if not document.file_name.endswith('.c'):
        await update.message.reply_text("Please send a valid C source file with a .c extension.")
        return

    # Save the uploaded file temporarily
    file_path = os.path.join(UPLOAD_FOLDER, document.file_name)
    file = await context.bot.get_file(document.file_id)
    await file.download_to_drive(file_path)

    # Notify the user that their file is being compiled
    await update.message.reply_text(f"Received `{document.file_name}`. Compiling now...")

    output_path = os.path.splitext(file_path)[0]  # Binary file name without extension

    try:
        # Compile the file with the required flags
        subprocess.run(
            ["gcc", file_path, "-o", output_path, "-lpthread", "-lz", "-static"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Send the compiled binary back to the user
        with open(output_path, "rb") as binary_file:
            await context.bot.send_document(update.message.chat.id, binary_file, filename=os.path.basename(output_path))

        await update.message.reply_text(f"Successfully compiled `{document.file_name}`.")
    
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode()
        await update.message.reply_text(f"Compilation failed for your file:\n\n{error_message}")

    finally:
        # Clean up source file and binary to save space
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(output_path):
            os.remove(output_path)

# Main function to run the bot
def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot_token = "7645973750:AAHpQkqwMsZjeV9qstfN13OaYAhDGHudCXc"
    application = Application.builder().token(bot_token).build()

    # Add command and file handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.FileExtension("c"), handle_c_file))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
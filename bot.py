# Import Required Libraries
import responses as responses
from telegram.ext import *
import numpy as np
from keras.preprocessing import image 
from keras.models import load_model
import joblib 
import os

# Chatbot commands
def start_command(update, context):
    update.message.reply_text("Thank you for choosing the Melanoma Checker Bot! Please upload a photo for it to be assessed!\n\nHowever, please note that the bot's results is not 100% accurate and thus you should still consult a doctor!")

def help_command(update, context):
    update.message.reply_text("If you need help, you can contact your physician or visit the nearest hospital!")

def handle_message(update, context):
    text = str(update.message.text).lower()
    response = responses.sample_responses(text)
    update.message.reply_text(response)

def handle_photo(update, context):
    # Get Image & Save To Images Folder
    photo = update.message.photo[-1].get_file()
    photo.download('image.jpg')
    
    # Process Image
    tensor = convert_imgpath_to_tensor('image.jpg')
    prediction = get_pred_from_img(tensor)
    response = f"The prediction for the image is {prediction}!\n\n"

    # Add description for disease
    if prediction == "melanoma":
        response += "Melanoma is a form of skin cancer that begins in the cells (melanocytes) that control the pigment in your skin. Please visit your nearest doctor or your physician as soon as possible for an actual diagnosis!"
    elif prediction == "nevus":
        response += "Nevus is a benign (not cancer) growth on the skin that is formed by a cluster of melanocytes, or in other words, a mole!"
    else:
        response += "Seborrheic Keratosis is a common noncancerous (benign) skin growth that does not require treatment!"
        
    # Send reply
    update.message.reply_text(response)

def error(update, context):
    print(f"Update {update} caused error {context.error}!")

# Functions for Analyzing Image
def convert_imgpath_to_tensor(imgpath):
    # Loads RGB image as PIL.Image.Image type
    img = image.load_img(imgpath, target_size = (224, 224))
    # Convert PIL.Image.Image type to 3D tensor with shape (224, 224, 3)
    x = image.img_to_array(img)
    # Convert 3D tensor to 4D tensor with shape (1, 224, 224, 3) and return 4D tensor
    return np.expand_dims(x, axis = 0)

# Get Predictions From An Image
def get_pred_from_img(img_tensor):
    # Import Models
    rn_imported = load_model("ResNet.h5")
    dt_imported = joblib.load("DecisionTree")
    rf_imported = joblib.load("RandomForest")

    # Get Predictions From The Models
    rf_dt_input = img_tensor.reshape(img_tensor.shape[0], img_tensor.shape[1] * img_tensor.shape[2] * img_tensor.shape[3])
    pred_rn = np.argmax(rn_imported.predict(img_tensor / 255.0))
    pred_rf = rf_imported.predict(rf_dt_input)
    pred_dt = dt_imported.predict(rf_dt_input)

    # Get Predictions
    labels = ["melanoma", "nevus", "keratoses"]
    List = [pred_rn, pred_rf[0], pred_dt[0]]
    if len(set(List)) < 3:
        return labels[max(set(List), key = List.count)]
    else:
        return "melanoma"

def main():
    # Initialise Robot
    TOKEN = "5195416897:AAF7TOGCfDYieijCsN4_b_10LpF6mCQUXcI"
    updater = Updater(TOKEN, use_context = True)
    dispatcher = updater.dispatcher

    # Add Handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
    dispatcher.add_error_handler(error)

    # Get User Responses
    PORT = int(os.environ.get('PORT', 5000))
    updater.start_webhook(listen = "0.0.0.0", port = int(PORT), url_path = TOKEN, webhook_url = 'https://melanoma-bot.herokuapp.com/' + TOKEN)
    updater.idle()

# Sequence when file is ran
if __name__ == "__main__":
    print("Bot started...")
    main()
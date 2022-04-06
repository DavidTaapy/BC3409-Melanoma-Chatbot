# Import Libararies
from datetime import datetime

def sample_responses(input_text):
    # To process capitalization
    user_message = str(input_text).lower()
    
    # Basic interations
    if user_message in ("hello", "hi", "sup"):
        return "Hey! How's it going?"

    if user_message in ("who are you", "who are you?"):
        return "I am Melanoma Checker Bot!"

    if user_message in ("time", "time?"):
        now = datetime.now()
        date_time = now.strftime("%d/%m/%y %H:%M:%S")
        return date_time

    return "I don't understand you! Please say again?"
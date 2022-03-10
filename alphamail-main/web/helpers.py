from flask import redirect, render_template, session
from functools import wraps

import pickle

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_ids(service, user_id='me', labels=[]):
    try:
        next_page_token = ''
        msgs_list = []
        while True:
            msgs = service.users().messages().list(userId=user_id, labelIds=labels, 
                                                   maxResults=500, 
                                                   pageToken=next_page_token).execute()
            msgs_list += msgs['messages']
            print(msgs_list)
            if 'nextPageToken' not in msgs.keys():
                break
            next_page_token = msgs['nextPageToken']
            print('hi')
        print(msgs_list)
        return [msg['id'] for msg in msgs_list]
    except Exception as error:
        print('An error occurred: %s' % error)


def detect_words(message):

    # List of relationship indicators, red flag indicators, sales words, and urgency words
    relationship = ["dear", "love", "regards", "sincerely", "best", "xoxo", "grateful", "thank", "please", "kind", "best regards", "hope", "wish"]
    red_flags = ["survey", "prize", "boba", "unsubscribe", "free", "sign up"]
    sales_words = ["buy", "purchase", "promotion", "sale", "$"]
    urgency_words = ["urgent", "overdue", "final notice", "confirm", "recent activity", "last chance", "parcel", "danger", "suspicious", "assessment", "grade", "important", "reminder", "concern", "ASAP"]

    # Creates the categories array
    categories = []
    categories.append(relationship)
    categories.append(red_flags)
    categories.append(sales_words)
    categories.append(urgency_words)

    # Initializes unkown data point
    unknown = [0, 0, 0, 0]

    i = 0

    # Updates unknown datapoint
    for category in categories:
        for word in category:
            if word in message:
                unknown[i] += 1
        i += 1
    
    return unknown

    # After running this program, an example of an unknown datapoint would look like [2,0,0,1,0], with the last index 
    # representing the importance score which has not been calculated yet.


def linear_regression():

    # Loads linear regression model
    reg = pickle.load(open('linear_regression.pickle', 'rb'))
    return reg

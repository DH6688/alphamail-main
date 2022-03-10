from bs4 import BeautifulSoup
import base64
import email
import re

import os
import base64
from base64 import urlsafe_b64decode

import html
import pickle
import numpy as np
import random

verbose = 0
random.seed(1)


def fix_urls(str):
    # Changes all URLs into shortened versions that only use the domains and subdomains
    return re.sub(r"(https?:\/\/[A-z0-9.-]*\/)\S+", r"\1", str)


def clean_text(str):
    formatted = " ".join(str.splitlines())
    return formatted
    # return str.replace(r"\r\n", r"\n")


def enhance_text_legacy(str, clean=True):
    # Helps format email from HTML to text
    lines = (line.strip() for line in str.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    body = ' \n '.join(chunk for chunk in chunks if chunk)
    if clean:
        body = fix_urls(body)
    return body


def text_to_list(str):
    # Finds all words and punctuation in text and returns them as a list

    # Converts \n char to a word in case escape commands cause issues
    str = re.sub(r"\n", "newlinechar", str)

    # Returns list of all words and punctuation in text
    return re.findall(r"[\w']+|[.,!?;]", str)

#########


def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def clean(folder_name):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in folder_name)


def parse_parts(message_id, parts, folder_name, service):
    """
    Utility function that parses the content of an email partition
    """
    if parts:
        for part in parts:
            filename = part.get("filename")
            mimeType = part.get("mimeType")
            body = part.get("body")
            data = body.get("data")
            file_size = body.get("size")
            part_headers = part.get("headers")
            if verbose >= 3:
                print(parts)
            if part.get("parts"):
                # recursively call this function when we see that a part
                # has parts inside
                parse_parts(message_id, part.get("parts"), folder_name, service)
            if mimeType == "text/plain":
                # if the email part is text plain
                if data and verbose >= 2:
                    text = urlsafe_b64decode(data).decode()
                    print(text)
            elif mimeType == "text/html":
                # if the email part is an HTML content
                # save the HTML file and optionally open it in the browser
                if not filename:
                    filename = "index.html"
                filepath = os.path.join(folder_name, filename)
                if verbose >= 3:
                    print("Saving HTML to", filepath)
                    with open(filepath, "wb") as f:
                        f.write(urlsafe_b64decode(data))
            else:
                # attachment other than a plain text or HTML
                for part_header in part_headers:
                    part_header_name = part_header.get("name")
                    part_header_value = part_header.get("value")
                    if part_header_name == "Content-Disposition":
                        if "attachment" in part_header_value:
                            # we get the attachment ID
                            # and make another request to get the attachment itself
                            print("Saving the file:", filename, "size:", get_size_format(file_size))
                            attachment_id = body.get("attachmentId")
                            attachment = service.users().messages() \
                                        .attachments().get(id=attachment_id, userId='me', messageId=message_id).execute()
                            data = attachment.get("data")
                            filepath = os.path.join(folder_name, filename)
                            if data and verbose >= 3:
                                with open(filepath, "wb") as f:
                                    f.write(urlsafe_b64decode(data))


def find_plain_text(message_id, parts, service):
    """
    Utility function that parses the content of an email partition
    """
    if parts:
        for part in parts:
            mimeType = part.get("mimeType")
            body = part.get("body")
            data = body.get("data")
            if part.get("parts"):
                # recursively call this function when we see that a part
                # has parts inside
                return find_plain_text(message_id, part.get("parts"), service)
            if mimeType == "text/plain":
                # if the email part is text plain
                if data:
                    text = urlsafe_b64decode(data).decode()
                    return text
    return "No plain text found."


def read_email(message_id, service):
    """
    This function takes Gmail API `service` and the given `message_id` and does the following:
        - Downloads the content of the email
        - Reads email and retrieves id, labels, metadata, and processed body text
    """
    msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    # parts can be the message body, or attachments
    if verbose >= 2:
        print(message_id)
    payload = msg['payload']
    if 'labelIds' in msg:
        labels = msg['labelIds']
    else:
        labels = []
    headers = payload.get("headers")
    snippet = msg.get('snippet')
    parts = payload.get("parts")
    folder_name = "email"
    has_subject = False
    metadata = {}
    if headers:
        # print(headers)
        # this section prints email basic info & creates a folder for the email
        for header in headers:
            name = header.get("name")
            value = header.get("value")
            if name.lower() == 'from':
                # we print the From address
                metadata['from'] = value
                if verbose >= 1:
                    print("From:", value)
            if name.lower() == "to":
                # we print the To address
                metadata['to'] = value
                if verbose >= 1:
                    print("To:", value)
            if name.lower() == "subject":
                # make our boolean True, the email has "subject"
                has_subject = True
                metadata['subject'] = value
                # make a directory with the name of the subject
                folder_name = clean(value)
                # we will also handle emails with the same subject name
                if verbose >= 3:
                    folder_counter = 0
                    while os.path.isdir(folder_name):
                        folder_counter += 1
                        # we have the same folder name, add a number next to it
                        if folder_name[-1].isdigit() and folder_name[-2] == "_":
                            folder_name = f"{folder_name[:-2]}_{folder_counter}"
                        elif folder_name[-2:].isdigit() and folder_name[-3] == "_":
                            folder_name = f"{folder_name[:-3]}_{folder_counter}"
                        else:
                            folder_name = f"{folder_name}_{folder_counter}"
                    os.mkdir(folder_name)
                    print("Subject:", value)
            if name.lower() == "date":
                # we print the date when the message was sent
                metadata['date'] = value
                if verbose >= 1:
                    print("Date:", value)
    if not has_subject and verbose >= 3:
        # if the email does not have a subject, then make a folder with "email" name
        # since folders are created based on subjects
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)

    if verbose >= 2:
        print("Labels:", labels)
    body_text = find_plain_text(message_id, parts, service)
    if verbose >= 1:
        print("="*50)
    return [message_id, labels, metadata, snippet, body_text]


def remove_punctuation(str):
    return str.translate(str.maketrans('', '', ',.!?'))


def freq_encode(str, dictionary):
    """
    Encodes the frequency of each word in the string into a vector based on dictionary list
    """
    encoding = [0] * len(dictionary)
    str = str.lower()
    words = str.split()
    for word in words:
        if word in dictionary:
            index = dictionary.index(word)
            encoding[index] += 1
    return encoding


def save_emails(emails, file_name='emails'):
    with open(file_name, 'wb') as f:
        pickle.dump(emails, f)


def load_emails(file_name='emails'):
    with open(file_name, 'rb') as f:
        emails = pickle.load(f)
    return emails


def load_dictionary(file_name='dict.txt'):
    with open(file_name) as f:
        dictionary = f.read().splitlines()
        # see https://stackoverflow.com/questions/3277503/how-to-read-a-file-line-by-line-into-a-list
    return dictionary


def determine_import(email):
    if 'IMPORTANT' in email[1]:
        return 1
    return 0


def generate_example(email, dictionary=None):
    """
    Creates a data point with one hot encoding
    against a dictionary
    """
    subject = email[2]['subject']
    subject = remove_punctuation(subject)
    importance = determine_import(email)
    encoding = None
    if dictionary is not None:
        encoding = freq_encode(subject, dictionary)
    return subject, encoding, importance


def save_dataset(dataset, file_name='dataset'):
    np.save(file_name, dataset)


def load_dataset(file_name='dataset.npy'):
    return np.load(file_name, allow_pickle=True)


######  legacy functions ######


def decode_legacy(txt):
    """
    Helps decode message from raw to human-readable text
    """
    labels = txt['labelIds']
    id = txt['id']
    # Get value of 'payload' from dictionary 'txt'
    payload = txt['payload']
    headers = payload['headers']

    # The Body of the message is in Encrypted format. So, we have to decode it.
    # Get the data and decode it with base 64 decoder.
    # print(payload)
    parts = payload.get('parts')[0]
    data = parts['body']['data']
    data = data.replace("-", "+").replace("_", "/")
    decoded_data = base64.b64decode(data)

    # Now, the data obtained is in lxml. So, we will parse
    # it with BeautifulSoup library
    soup = BeautifulSoup(decoded_data, "lxml")
    body = soup.body.get_text()
    body = enhance_text(body)

    # Returns headers as a list of dictionaries (each dictionary is {'name': [key], 'Value': ['value']}) and body text
    return [id, labels, headers, body]


def get_msg_legacy(email_id, service, user_id='me', format='full'):
    try:
        # Retrieves message based on ID
        txt = service.users().messages().get(userId=user_id, id=email_id, format=format).execute()
        # Returns decoded message
        return decode_legacy(txt)

    except Exception as error:
        pass


def get_msgs_full_legacy(ids, service, user_id='me'):
    try:
        emails = []
        # Gets messages based on email ID
        for id in ids:
            if verbose >= 1:
                print(id)
            msg = get_msg_legacy(id, service, user_id)
            if msg is None and verbose >= 1:
                print("No msg:" + id)
            else:
                emails.append(get_msg_legacy(id, service, user_id))
        return emails
    except Exception as error:
        print('An error occurred: %s' % error)


def get_msgs_select_legacy(ids, service, params, user_id='me'):
    # Retrieves full email messages
    emails = []
    msgs_full = get_msgs_full_legacy(ids, service, user_id)
    if verbose >= 1:
        print("Number of messages: " + str(len(msgs_full)))
    # Filters to specific metadata
    for msg in msgs_full:
        headers = msg[2]
        metadata = {}
        for d in headers:
            if d['name'] in params:
                metadata[d['name']] = d['value']
        emails.append([msg[0], msg[1], metadata, msg[3]])
    return emails

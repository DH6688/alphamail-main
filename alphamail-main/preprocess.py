import helpers
import html
import numpy as np
import random

verbose = 0
random.seed(1)


def get_ids(service, user_id='me', labels=[]):
    """
    Retrieves all IDs of emails by parsing through each
    page of email IDs given an API connection.
    """
    try:
        next_page_token = ''
        msgs_list = []
        while True:
            msgs = service.users().messages().list(userId=user_id, labelIds=labels,
                                                   maxResults=500,
                                                   pageToken=next_page_token).execute()
            msgs_list += msgs['messages']
            if 'nextPageToken' not in msgs.keys():
                break
            next_page_token = msgs['nextPageToken']
        return [msg['id'] for msg in msgs_list]
    except Exception as error:
        print('An error occurred here: %s' % error)


def read_all_emails(ids, service):
    all_email = []
    count = 0
    if verbose >= 0:
        print("Total emails:", len(ids))
    for id in ids:
        email = helpers.read_email(id, service)
        email[3] = html.unescape(email[3])
        email[4] = helpers.clean_text(email[4])
        email[4] = helpers.fix_urls(email[4])
        if verbose >= 2:
            print(email)
        all_email.append(email)
        count += 1
        if count % 50 == 0:
            print("Current email count:", count, "(", count * 100 / len(ids), ")")
    # helpers.save_emails(all_email)
    return all_email


def generate_dataset(email_path='emails', dict_path=None):
    dataset = []
    emails = helpers.load_emails(email_path)
    dictionary = helpers.load_dictionary(dict_path) if dict_path is not None else None
    count = 0
    for email in emails:
        subject, encoding, importance = helpers.generate_example(email, dictionary)
        dataset.append(encoding + [importance]) if dict_path is not None else dataset.append([subject, importance])
        count += 1
        if count % 50 == 0:
            print(count)
    dataset = np.array(dataset, dtype=object)
    # helpers.save_dataset(dataset)
    return dataset  # use terminal to convert to numpy and save as file


def create_training_set(dataset, start, end):
    indices = np.arange(len(dataset))
    random.shuffle(indices)  # need to unrandomize for manual evaluation
    X = np.array(dataset[indices[start:end], :-1], dtype='U')
    Y = np.array(dataset[indices[start:end], -1:], dtype='i')
    return X, Y




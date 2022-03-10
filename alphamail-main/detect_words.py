def detect_words(message):
    relationship = ["dear", "love", "regards", "sincerely", "best", "xoxo", "grateful", "thank", "please", "kind", "best regards", "hope", "wish"]
    red_flags = ["survey", "prize", "boba", "unsubscribe", "free", "sign up"]
    sales_words = ["buy", "purchase", "promotion", "sale", "$"]
    urgency_words = ["urgent", "overdue", "final notice", "confirm", "recent activity", "last chance"]

    categories = []
    categories.append(relationship)
    categories.append(red_flags)
    categories.append(sales_words)
    categories.append(urgency_words)

    unknown = [0, 0, 0, 0, 0]

    i = 0
    for category in categories:
        for word in category:
            if word in message:
                unknown[i] += 1
        i += 1
    
    return unknown
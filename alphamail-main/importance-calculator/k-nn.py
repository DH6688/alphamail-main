import math
# First index represents number of personal relationship phrases multiplied by 1
# Second index represents number of red flags multiplied by 5
# Third index represents number of sales words multiplied by 10
# Fourth index represents number of urgency words multiplied by 5
# Fifth index represents number of words that say unsubscribe multiplied by 100
# Sixth index represents class 1 = important 0 = unimportant

training = [[3,0,0,0,0,1],[0,3,3,0,100,0],[0,20,30,0,100,0],[3,0,0,10,0,1],[3,10,20,5,100,0],[3,0,0,10,0,1],[1,20,20,5,100,0],[3,0,0,0,0,1],[1,20,20,5,100,0],[2,0,0,0,0,1]]
unknown = [3,0,0,30,0]

important_distance = 0
unimportant_distance = 0

for datapoint in training:
    
    a2 = datapoint[0]
    a1 = unknown[0]
    b2 = datapoint[1]
    b1 = unknown[1]
    c2 = datapoint[2]
    c1 = unknown[2]
    d2 = datapoint[3]
    d1 = unknown[3]
    e2 = datapoint[4]
    e1 = unknown[4]
    distance = math.sqrt((a2-a1)**2+(b2-b1)**2+(c2-c1)**2+(d2-d1)**2+(e2-e1)**2)
    
    if datapoint[5] == 1:
        important_distance += distance
    else:
        unimportant_distance += distance

score = unimportant_distance - important_distance
print(score)


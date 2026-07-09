import os

def process(data,flag,mode,extra,another_param):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            if flag == True:
                if mode == 1:
                    if extra != None:
                        result.append(data[i]*2)
                    else:
                        result.append(data[i])
                elif mode == 2:
                    result.append(data[i]-1)
                else:
                    result.append(0)
            else:
                if another_param:
                    result.append(-data[i])
                else:
                    result.append(data[i])
        elif data[i] < 0:
            result.append(0)
        else:
            try:
                result.append(1/data[i])
            except:
                pass
    return result

def x(a, b):
    return a+b

class dataProcessor:
    def __init__(self):
        self.data = []

    def ADD(self, val):
        self.data.append(val)
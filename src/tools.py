#Class to append messages to log files
class Logger:
    def __init__(self):            
        pass

    def to_file(self, kind=None, message=None):   
        #Verify variables     
        if message is None:
            message = "!!No message!!"
        if kind is None:
            kind = "error"
            message = message.join("!!No kind informed!!")

        #Error messages
        if kind == "error":
            with open("error_log.txt", 'a') as f:
                f.write(message+'\n')
        #Event messages
        elif kind == "event":
            with open("event_log.txt", 'a') as f:
                f.write(message+'\n')

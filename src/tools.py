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



class Encoder:
    def __init__(self):
        self.log = Logger()

    def to_bytes(self, raw_msg=None):

        #Avoid data collision between function instances
        if raw_msg is None:
            raw_msg = b"!!DEFAULT!!"

        #If list, concatenate to semicolon separated string and convert
        if isinstance(raw_msg, list):
            #print('list')
            self.log.to_file(kind="event", message="list")
            all_bytes = "!!DEFAULT!!"
            try:
                for n in raw_msg:
                    all_bytes = all_bytes + ';' + n

                all_bytes = all_bytes + ';' + "!!DEFAULT!!"
            except Exception as ex:
                self.log.to_file(kind="error", message=str(ex))

            return all_bytes.encode("utf-8")
        
        #If string convert directly
        elif isinstance(raw_msg, str):
            #print('string')
            self.log.to_file(kind="event", message="string")
            return raw_msg.encode("utf-8")    
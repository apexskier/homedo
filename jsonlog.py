import json, os

class jsonLog(object):
    def __init__(self, filename):
        self.filename = filename + '.json'
        self.new = False
        try:
            f = open(self.filename, 'r')
            try:
                d = json.loads(f.read())
                if not d:
                    self.new = True
            except ValueError:
                print("Not valid JSON.")
                return None
            f.close()
        except IOError:
            f = open(self.filename, 'w')
            f.write('[]')
            f.close()
            self.new = True

    def log(self, data):
        try:
            with open(self.filename, 'rb+') as f:
                f.seek(-1, os.SEEK_END)
                f.truncate()
                f.close()
            with open(self.filename, 'a') as f:
                if not self.new:
                    f.write(',')
                f.write(json.dumps(data))
                f.write(']')
                f.close()
                self.new = False
        except IOError:
            print("Problem with jsonlog file.")

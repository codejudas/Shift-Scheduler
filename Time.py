#Object which holds a time in the format hh:mm
import pickle

class Time:

    def __init__(self, hour=0, minute=0):
        '''
            24 hour time
        '''
        #add support for building with string input, treat hour as string if tpe string and minute == 0
        if type(hour) == str:
            res= self.parseTime(hour)
            if res == -1:
                print("Invalid input string")
                self.hour = 0
                self.minute = 0
        else:
            self.hour = hour
            self.minute = minute

        if self.isValid() == False:
            print("Invalid Time")
            self.hour = 0
            self.minute = 0

    def isValid(self):
        '''Checks to see time is valid'''
        ret = (True and self.hour>=0 and self.hour <= 23)
        return (ret and self.minute >=0 and self.minute < 60) 

    def parseTime(self, time):
        '''
            takes a string in format hh:mm or h:mm and sets this Time object to that time
            supports h:mm (24 hour) or hh:mm(24 hour)
            also supports h:mm pm or hh:mm pm
        '''
        if type(time) != str:
            return -1

        if len(time) > 8 or len(time) < 3:
            return -1

        sep = time.find(':')
        if sep not in [1,2]:
            #enforces "h:mm" or "hh:mm"
            return -1

        hour = time[:sep]
        minute = time[sep+1:sep+3]

        try:
            hour = int(hour)
            minute = int(minute)
        except:
            return -1

        if time[-2:] == "pm": #get last two characters
            if hour < 12:
                hour += 12
            elif hour >= 13:
                return -1

        if hour not in range(0,24):
            return -1

        if minute not in range(0,60):
            return -1

        self.hour = hour
        self.minute = minute

        return 1

    def __cmp__ (self, otherTime):
        '''Returns -1 if this is before otherTime, 0 if they are equal, 1 if it is later'''
        if otherTime.__class__.__name__ != "Time":
            return 1
        if self.hour == otherTime.hour:
            if self.minute == otherTime.minute:
                return 0
            elif self.minute > otherTime.minute:
                return 1
            else:
                return -1

        elif self.hour > otherTime.hour:
            return 1
        else:
            return -1

    def __lt__(self,other):
        res = self.__cmp__(other)
        if res >= 0:
            return False
        else:
            return True

    def __eq__(self,other):
        res = self.__cmp__(other)
        if res == 0:
            return True
        return False

    def __le__(self, other):
        res = self.__cmp__(other)
        if res > 0:
            return False
        return True

    def __hash__(self):
        result = self.hour*100
        result += self.minute
        return result

    def __str__(self):
        '''prints in human-readable format'''
        result = ""
        if self.hour >= 12:
            if self.hour > 12:
                result = "%d:%02dpm"%(self.hour-12, self.minute)
            else:
                result = "%d:%02dpm"%(self.hour,self.minute)
        else:
            result = "%d:%02d"%(self.hour,self.minute)

        return result

    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        #used to convert when pickling
        return "%d:%02d"%(self.hour, self.minute)
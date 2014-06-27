#Rule Class
import pickle
from Time import Time

class Rule:
    '''
        a datastructure to hold a rule
        essentially a dictionary whose values can be T/F, numbers or list of numbers
    '''

    def __init__(self, **kwargs):
        '''
            sets a new rule where rule is specified in **kwargs as list of key-val pairs
            ex: Evan.setRule(lunch=False) // means not available for all lunchshifts
            ex: Evan.setRule(dinner=True, time=5, weekday=0) //means available at 5 for dinner shifts on monday

            Accepted keys:
                maxShifts = num Indicates how many shifts a person wants to works. This key should be by itself in its own rule
                maxShiftsPW = num indicates max number of shifts an employee is willing to work per week

                exclude = days: If exclude keyword is in Rule, the specified days will be excluded from scheduling, Can be used with lunch/dinner to only exclude part of day

                lunch = True if available for lunch shifts, False if available for dinner shift, ommit for available for both

                time = string "h:mm" hour at which employee is available (used with lunch or dinner True or else will match either)
                weekday = 0-6 indicating which day of the week, 0=Monday, 6=Sunday
                weeknum = 1-5, applies rule to a specific week of the month
                daynum = 1-31, applies rule to a specific day of the month

                weekday, weeknum, daynum can also be lists of same values ie weekday = [0,2] means rule applies for Mon & Tues

                If daynum then don't use weeknum or weekday
                if weekday, dont use daynum, optionally use weeknum to restrict range
                if weeknum, use with weekday to restrict range
        '''
        ##TODO IMPLEMENT MORE CHECKING FOR UPDATED SPEC##
        self.rule = {}
        self.fancyNames = {"maxshifts" : "Maximum Shifts Allowed Each Month",
                            "maxshiftspw" : "Maximum Shifts Allowed Each Week",
                            "lunch" : "Lunch Shift",
                            "dinner" : "Dinner Shifts",
                            "both" : "Lunch or Dinner",
                            "time" : "Available After",
                            "weekday" : "Weekdays Available",
                            "weeknum" : "Weeks Available (1 to 5)",
                            "daynum" : "Available On"}

        self.weekdayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        #TODO PRINT WEEKNUM AS WEEKDAY BOUNDS FOR READABILITY

        for key in kwargs:
            lowerKey = key.lower()
            val = kwargs[key]
            print("%s:%s"%(lowerKey, val))

            if lowerKey == "maxshifts" and val >= 0:
                if len(kwargs) != 1:
                    print("maxShifts must appear in its own rule by itself")
                    input()
                else:
                    self.rule[lowerKey] = val
                    break

            if lowerKey == "maxshiftspw" and val >= 0:
                if len(kwargs) != 1:
                    print("maxShiftsPW must appear in its own rule by itself")
                    input()
                else:
                    self.rule[lowerKey] = val
                    break

            if lowerKey == "exclude":
                if type(val) == int:
                    if val in range(1,32):
                        self.rule[lowerKey] = [val]
                    else:
                        print("exclude field must be 1-31")
                        input()

                elif type(val) == list:
                    #is true if all elems on list val are integers

                    if self.isAllInts(val):
                        #is true if all elems in list val are within specified range
                        if self.isValid(val, range(1,32)):
                            self.rule[lowerKey] = val
                        else:
                            print("exclude field list must all be within 1-31")
                            input()
                    else:
                        print("exclude field list must all be integers")
                        input()

                break #exclude field should appear by itself


            if lowerKey == "lunch":
                if val == True or val == False:
                    self.rule[lowerKey]=val
                else:
                    print("lunch field must be True or False")
                    input()

            elif lowerKey == "time":
                if type(val)==str:
                    time = Time()
                    res = time.parseTime(val)
                    if res != -1:
                        self.rule[lowerKey] = time
                    else:
                        print("time field must be string in format (24 hour) hh:mm or h:mm (optional pm)")
                        input()

                elif val.__class__.__name__ == "Time":
                    if val.isValid():
                        self.rule[lowerKey] = val
                    else:
                        print("Invalid time")
                        input()

            elif lowerKey == "weekday":
                if type(val) == int:
                    if val in range(0,7):
                        self.rule[lowerKey] = [val]
                    else:
                        print("weekday field must be 0-6")
                        input()

                elif type(val) == list:
                    #is true if all elems on list val are integers
                    if self.isAllInts(val):
                        #is true if all elems in list val are within specified range
                        if self.isValid(val, range(0,7)): 
                            self.rule[lowerKey] = val
                        else:
                            print("weekday field list must all be within 0-6")
                            input()
                    else:
                        print("weekday field list must all be integers")
                        input()


            elif lowerKey == "weeknum":
                if type(val) == int:
                    if val in range(1,7):
                        self.rule[lowerKey] = [val]
                    else:
                        print("weeknum field must be 1-5")
                        input()

                elif type(val) == list:
                    #is true if all elems on list val are integers

                    if self.isAllInts(val):
                        #is true if all elems in list val are within specified range
                        if self.isValid(val,range(1,7)):
                            self.rule[lowerKey] = val
                        else:
                            print("weeknum field list must all be within 1-5")
                            input()
                    else:
                        print("weeknum field list must all be integers")
                        input()

            elif lowerKey == "daynum":
                if type(val) == int:
                    if val in range(1,32):
                        self.rule[lowerKey] = [val]
                    else:
                        print("daynum field must be 1-31")
                        input()

                elif type(val) == list:
                    #is true if all elems on list val are integers
                    if self.isAllInts(val):
                        #is true if all elems in list val are within specified range
                        if self.isValid(val, range(1,32)):
                            self.rule[lowerKey] = val
                        else:
                            print("daynum field list must all be within 1-31")
                            input()
                    else:
                        print("daynum field list must all be integers")
                        input()

    def getDict(self):
        return self.rule

    def isAllInts(self,input_list):
        for e in input_list:
            if type(e) != int:
                print(e)
                return False
        return True

    def isValid(self, input_list, r):
        for e in input_list:
            if e not in r:
                print(e)
                return False
        return True

    def __str__(self):
        result = ""
        both = False
        if "lunch" not in self.rule.keys() and "maxshifts" not in self.rule.keys() and "maxshiftspw" not in self.rule.keys() and "exclude" not in self.rule.keys():
            both = True
            title = self.fancyNames["both"]
            result += "  -%s\n"%(title)

        for key in self.rule:
            if key == "lunch" and self.rule["lunch"] == False:
                title = self.fancyNames["dinner"]
                result += "  -%s\n"%title

            elif key == "lunch":
                title = self.fancyNames["lunch"]
                result += "  -%s\n"%title

            elif key == "exclude":
                days = str(self.rule["exclude"])[1:-1]
                result += "  -Not available to work on days: %s\n"%days

            elif key == "weekday":
                result += "  -"
                for i in range(0, len(self.rule["weekday"])):
                    if i == (len(self.rule["weekday"]) -1):
                        result += "%s"%self.weekdayNames[self.rule["weekday"][i]]
                    else:
                        result += "%s, "%self.weekdayNames[self.rule["weekday"][i]]

                result += "\n"

            else:
                title = self.fancyNames[key]
                result += "  -%s : %s \n"%(title, str(self.rule[key]))

        result += "\n"
        return result

    def __repr__(self):
        return self.__str__()

    def hasKey(self, key):
        if key in self.rule.keys():
            return True
        return False

    def save(self, file, num, info=False):
        '''
            @param file: a file poiner open in "wb" mode
            @param num: the number of the rule (used purely for printing output)
            @param info: T/F wether to print additional info while saving
        '''
        pickle.dump(len(self.rule.keys()), file)
        for k in self.rule.keys():
            if info: print("      k: "+str(k)+", val: "+str(self.rule[k]))
            pickle.dump(k, file)
            if k == "time":
                s = str(self.rule[k])
                pickle.dump(s, file)
            else: 
                pickle.dump(self.rule[k],file)

        if info: print("      Saved rule %d (%d items)"%(num+1, len(self.rule.keys())))

    def load(self, file, num, info=False):
        '''
            @param file: a file poiner open in "rb" mode
            @param num: the number of the rule (used purely for printing output)
            @param info: T/F wether to print additional info while loading
        '''
        try:
            length = pickle.load(file)
            self.rule = {}
            for i in range(0, length):
                tmp_key = pickle.load(file)
                if tmp_key == "time":
                    s = pickle.load(file)
                    t = Time(s)
                    tmp_val = t
                else:
                    tmp_val = pickle.load(file)
                self.rule[tmp_key] = tmp_val

            if info: print("      Loaded rule %d (%d items)"%(num+1, length))
            return True

        except Exception as e:
            print("Error: %s while loading rule %d (%d items)"%(str(e), num+1, length))
            raise e
            return False

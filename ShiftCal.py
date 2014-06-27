#Shift Calendar Class
#Calendar built on current month which holds all information about shifts.
import calendar
import pickle
import traceback,sys

from Time import Time
from Employee import Employee, Rule
#DAYS
MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

#Use as Lunch flag in ShiftDay function calls
#ex ShiftDay.findShift(time, LUNCH) or ShiftDay.findShift(time, DINNER)
LUNCH = True
DINNER = False


#Weekday Numbers to Day Names
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_NAMES = ["Dummy", "January","February","March","April","May","June","July","August","September","October","November","December"]

class ShiftDay:

    def __init__(self, weekday, dayNum, weeknum):
        self.dayNum = dayNum
        self.weekday = weekday
        self.weeknum = weeknum

        self.lunchShifts = {}
        self.dinnerShifts = {}

    def save(self, file, info=False):
        '''
            Saves a shiftDay
            @param file: a file pointer open in "wb" mode
            @params info: T/F whether to print additional info while saving.
        '''
        if info: print("  Saving shifts for day %d..."%self.dayNum)
        pickle.dump(self.dayNum, file)
        pickle.dump(self.weekday, file)
        pickle.dump(self.weeknum, file)
        tmp = {}
        for t in self.lunchShifts.keys():
            t_s = str(t)
            if self.lunchShifts[t] != None: tmp[t_s] = self.lunchShifts[t].getName()   
            else: tmp[t_s] = None

        pickle.dump(tmp, file)
        if info: print("    Saved lunch shifts:%s"%tmp)

        tmp = {}
        for t in self.dinnerShifts.keys():
            t_s = str(t)
            if self.dinnerShifts[t] != None: tmp[t_s] = self.dinnerShifts[t].getName()
            else: tmp[t_s] = None

        pickle.dump(tmp, file)
        if info: print("    Saved dinner shifts:%s"%tmp)
        return True

    def load(self, file, emp_dict, correct_day, info = False):
        '''
            Loads a shiftDay
            @param file: a file pointer open in "rb" mode & at appropriate place to load correct shiftday
            @params info: T/F whether to print additional info while saving.
        '''
        try:
            if info: print("    Loading day %s"%str(correct_day+1))
            daynum = pickle.load(file)
            if info: print("      Read daynum: %d"%daynum)
            weekday = pickle.load(file)
            if info: print("      Read weekday: %d"%weekday)
            weeknum = pickle.load(file)
            if info: print("      Read weeknum: %d"%weeknum)
            if info: print("      Loaded shift attributes...")
            self.dayNum = daynum
            self.weekday = weekday
            self.weeknum = weeknum

            if daynum != (correct_day+1):
                print("\nError: Day number mismatch, was %d, should be %d"%(dayNum, i))
                return False

            tmp = pickle.load(file)
            if info: print("      Read lunch shifts:%s"%tmp)
            #Times in tmp dict are in string format, here we restore Time objects
            self.lunchShifts = {}
            for t in tmp.keys():
                emp_name = tmp[t]
                if emp_name == None: self.lunchShifts[Time(t)] = None
                else: self.lunchShifts[Time(t)] = emp_dict[emp_name]

            tmp = pickle.load(file)
            if info: print("      Read dinner shifts:%s"%tmp)
            self.dinnerShifts = {}
            for t in tmp.keys():
                emp_name = tmp[t]
                if emp_name == None: self.dinnerShifts[Time(t)] = None
                else: self.dinnerShifts[Time(t)] = emp_dict[emp_name] #restore Time object & employee object

            return True

        except Exception as e:
            print("Error (day %d): %s"%(correct_day,str(e)))
            raise e
            return False


    def addLunchShift(self, time):
        '''Adds a lunch shift if one doesnt already exist for that time
           time is an object defined in time.py
        '''
        if time not in self.lunchShifts.keys():
            self.lunchShifts[time] = None
            self.printTimestamp(time, "Shift added at ")
        else:
            self.printTimestamp(time, "Shift already exists at ")

    def setLunchShift(self, time, person):
        '''
            Sets self.lunchShifts[time] = person
            If previous val of self.lunchShifts[time] was an employee, his shift count is decremented
            Finally increment new employee's shift count if person is not None

            @params time: Time object representing beginning of shift
            @params person: Employee object assigned to shift or None for empty shift
        '''
        if time in self.lunchShifts.keys():
            if self.lunchShifts[time] != None:
                self.lunchShifts[time].removeShift(self.weeknum)
            self.lunchShifts[time] = person
            if person != None:
                person.addShift(self.weeknum)
            self.printTimestamp(time, "Assigned %s to shift "%person)
        else:
            self.printTimestamp(time, "Could not find shift ")

    def removeLunchShift(self, time):
        '''Deletes a lunch shift'''
        if time in self.lunchShifts.keys():
            if self.lunchShifts[time] != None:
                self.lunchShifts[time].removeShift(self.weeknum)
            del(self.lunchShifts[time])
            self.printTimestamp(time, "Shift deleted ")
        else:
            self.printTimestamp(time, "Shift does not exist ")

    def addDinnerShift(self, time):
        '''Adds a dinner shift if one doesnt already exist for that time
           time is an object defined in time.py
        '''
        if time not in self.dinnerShifts.keys():
            self.dinnerShifts[time] = None
            self.printTimestamp(time, "Shift added at ")

        else:
            self.printTimestamp(time, "Shift already exists at ")

    def setDinnerShift(self, time, person):
        '''
            Sets self.dinnerShifts[time] = person
            If previous val of self.dinnerShifts[time] was an employee, his shift count is decremented
            Finally increment new employee's shift count if person is not None

            @params time: Time object representing beginning of shift
            @params person: Employee object assigned to shift or None for empty shift
        '''
        if time in self.dinnerShifts.keys():
            if self.dinnerShifts[time] != None:
                self.dinnerShifts[time].removeShift(self.weeknum) #update replaced person's shift count

            self.dinnerShifts[time] = person
            if person != None:
                person.addShift(self.weeknum) #update new employees shift count

            self.printTimestamp(time, "Assigned %s to shift "%person)
        else:
            self.printTimestamp(time, "Could not find shift: ")

    def removeDinnerShift(self, time):
        '''Deletes a dinner shift'''
        if time in self.dinnerShifts.keys():
            if self.dinnerShifts[time] != None:
                self.dinnerShifts[time].removeShift(self.weeknum)
            del(self.dinnerShifts[time])
            self.printTimestamp(time, "Shift deleted ")
        else:
            self.printTimestamp(time, "Shift does not exist ")

    def isDinnerFull(self):
        '''Returns true if all shifts filled for dinner'''
        for key in self.dinnerShifts.keys():
            if self.dinnerShifts[key] == None:
                return False
        return True

    def isLunchFull(self):
        '''Returns true if all shifts filled for lunch'''
        for key in self.lunchShifts.keys():
            if self.lunchShifts[key] == None:
                return False
        return True

    def getEmpShifts(self, emp):
        '''
            Returns list of shifts that emp is assigned for
            @params emp: Employee object to match

            @return: list of shifts employee is assigned to on this day in format [(lunch1, time1), (lunch2, time2),...]
        '''
        res = []
        for t in self.lunchShifts.keys():
            if self.lunchShifts[t] == emp:
                res.append((LUNCH, t))

        for t in self.dinnerShifts.keys():
            if self.dinnerShifts[t] == emp:
                res.append((DINNER, t))
        return res

    def findShift(self, time, lunch=False):
        '''
            Returns assigned employee if shift exists or -1 if shift does not exist
        '''
        if lunch:
            for key in self.lunchShifts.keys():
                print("time: %s, key: %s"%(time,key))
                print("time==key : %s"%(time==key))
                if time == key:
                    return self.lunchShifts[key]
            return -1
        else:
            for key in self.dinnerShifts.keys():
                print("time: %s, key: %s"%(time,key))
                if time == key:
                    return self.dinnerShifts[time]
            return -1

    def clearDinner(self):
        '''clears all dinner shifts'''
        for shift in self.dinnerShifts.keys():
            val = self.dinnerShifts[shift]
            if val != None: 
                val.removeShift(self.weeknum) #updates employee object
                self.dinnerShifts[shift] = None #unassign employee

        print("All dinner cleared deleted for %d %s"%(self.dayNum, DAY_NAMES[self.weekday]))

    def clearLunch(self):
        '''clears all lunch shifts'''
        for shift in self.lunchShifts.keys():
            val = self.lunchShifts[shift]
            if val != None: 
                val.removeShift(self.weeknum)
                self.lunchShifts[shift] = None

        print("All lunch shifts cleared for %d %s"%(self.dayNum, DAY_NAMES[self.weekday]))

    def clearShift(self, shift, lunch=False):
        '''
            Sets specified shift to None if that shift exists
        '''
        if lunch: self.setLunchShift(shift, None)
        else: self.DinnerShift(shift,None)

    def printShift(self, lunch = False):
        if lunch:
            res = ""
            sorted_keys = list(self.lunchShifts.keys())
            sorted_keys.sort()
            for t in sorted_keys:
                res+="\t%s - %s\n"%(t, self.lunchShifts[t])
            return res
        else:
            res = ""
            sorted_keys = list(self.dinnerShifts.keys())
            sorted_keys.sort()
            for t in sorted_keys:
                res+="\t%s - %s\n"%(t, self.dinnerShifts[t])
            return res

    def printTimestamp(self, time,  msg = ""):
            return msg + "%d:%02d (%d %s)"%(time.hour,time.minute,self.dayNum, DAY_NAMES[self.weekday])

    def getAllShifts(self):
        '''
            @return: sorted list of shift times in format [[lunchtime1, lunchtime2],[dinnertime1,dinnertime2]]
        '''
        ret = []
        lunchTimes = sorted(self.lunchShifts.keys())
        dinnerTimes = sorted(self.dinnerShifts.keys())
        ret.append(lunchTimes)
        ret.append(dinnerTimes)
        return ret

    #PRobably unused, can delete
    def getEmptyShifts(self):
        '''
            @return: sorted list of shift times in format [[lunchtime1, lunchtime2],[dinnertime1,dinnertime2]]
                     a shift is only included if it is empty
        '''
        ret = []
        lunchTimes = []
        for lt in sorted(self.lunchShifts.keys()):
            if self.lunchShifts[lt] == None:
                lunchTimes.append(lt)
        ret.append(lunchTimes)
        dinnerTimes = []
        for dt in sorted(self.dinnerShifts.keys()):
            if self.dinnerShifts[dt] == None:
                dinnerTimes.append(dt)
        ret.append(dinnerTimes)
        return ret

    def getNextEmptyShift(self):
        '''
            @return: the next empty shift in form [lunch, shiftTime], if no empty shifts, return None
        '''
        for lt in sorted(self.lunchShifts.keys()):
            if self.lunchShifts[lt] == None:
                return [True, lt]
        for dt in sorted(self.dinnerShifts.keys()):
            if self.dinnerShifts[dt] == None:
                return [False, dt]
        return None

    def __str__(self):
        res = "lunch: %s\ndinner%s"%(self.lunchShifts,self.dinnerShifts)
        return res

class ShiftCalendar:

    def __init__(self, month, year):
        self.month = month
        self.year = year

        cal = calendar.Calendar()

        self.numDays = max(list(cal.itermonthdays(self.year, self.month))) #get number of days in month
        self.firstDay = calendar.weekday(year,month,1) #mon=0 - sun=6
        self.numWeeks = 5 if self.numDays>28 else 4

        self.days = [] #list holding all ShiftDays

        day = self.firstDay #mon:0 - sun:6

        for i in range(0, self.numDays):
            self.days.append(ShiftDay(day%7, i+1, day//7))
            day += 1

    def getDay(self, dayNum):
        '''
            @params dayNum: integer between 1-numDays
            @return: ShiftDay for that day
        '''
        if dayNum <= 0 or dayNum > self.numDays:
            return None
        return self.days[dayNum-1] #zero indexed

    def save(self, f, info=False):
        '''
            Saves shiftCal and all shiftDays included in month to filename
            @params f: open file pointer in "wb" mode
            @params info: T/F whether to print additional info while saving.
        '''
        print("Saving Calendar data...")
        pickle.dump(self.month, f)
        pickle.dump(self.year, f)
        pickle.dump(self.numDays, f)
        pickle.dump(self.firstDay, f)
        pickle.dump(self.numWeeks, f)
        if info: print("  Saved calendar attributes")

        #Save all shift days in order
        print("  Saving shifts data...")
        for d in self.days:
            d.save(f, info)
            if info: print("")
        return True

    def load(self, f, emp_dict, info=False):
        '''
            Loads saved shiftCal and all shiftDays included in the month from filename
            @params f: a string
            @params emp_dict: dictionary mapping employee names to employee objects, used to reconstruct employee references
            @params info: T/F whether to print additional info while saving.
            @returns True if load succeeded, False if error.
        '''
        try:
            print("Loading Calendar data...")
            self.month = pickle.load(f)
            if info: print("  Read month: %d"%self.month)
            self.year = pickle.load(f)
            if info: print("  Read year: %d"%self.year)
            self.numDays = pickle.load(f)
            if info: print("  Read num days: %d"%self.numDays)
            self.firstDay = pickle.load(f)
            if info: print("  Read first day: %d"%self.firstDay)
            self.numWeeks = pickle.load(f)
            if info: print("  Read num weeks: %d"%self.numWeeks)
            print("  Loaded calendar attributes")

            print("  Loading shifts data...")
            self.days = []
            for i in range(0, self.numDays):
                d = ShiftDay(0,0,0) #create dummy day
                if d.load(f, emp_dict, i, info):
                    self.days.append(d)
                else:
                    print("\nError: Failed to load day %d."%i)
                    return False
                if info: print("")

            return True

        except Exception as e:
            print("An error occurred while loading shift calendar data...")
            print("Error: "+ str(e))
            traceback.print_exc(file=sys.stdout)
            return False        

    def isComplete(self):
        '''Returns true if all shifts of every day are filled'''
        for shiftday in self.days:
            temp = shiftday.isDinnerFull()
            temp = temp and shiftday.isLunchFull()
            if temp == False:
                return False
        return True

    def setShiftsByDay(self, weekday, shifts, lunch = False):
        '''sets all weekdays to empty shift, if lunch is true then sets lunch shifts, otherwise sets dinner shifts
           ie weekday = 0 (monday), shifts [time1, time2]
        '''
        if weekday in range(0,7):
            for i in range(weekday-self.firstDay, self.numDays, 7):
                #print("i=%d"%i)
                if i <= 0: 
                    continue #fix negative indexing from subtracting firstDay
                shiftday = self.days[i]
                #print("Got day %d"%i)
                if lunch == False:
                    for time in shifts:
                        shiftday.addDinnerShift(time)
                else:
                    for time in shifts:
                        shiftday.addLunchShift(time)

            print("%ss %s shifts set to: %s"%(DAY_NAMES[weekday], 'lunch' if lunch else 'dinner', shifts))

    def setSingleDay(self, day, shifts, lunch = False):
        '''
            Sets a single day to empty shift (creates new shifts)
            day is the day number(1-31)
        '''
        if day >= 1 and day <= self.numDays:
            day -= 1 #offset for list index of self.days
            shiftday = self.days[day]
            if lunch:
                for time in shifts:
                    shiftday.addLunchShift(time)
            else:
                for time in shifts:
                    shiftday.addDinnerShift(time)

    def getShifts(self, day, lunch=False):
        '''
            Get all shifts for a day lunch or dinner
        '''
        if day >= 1  and day <= self.numDays:
            day -= 1
            shiftday = self.days[day]
            ret = []
            if lunch and len(shiftday.lunchShifts)> 0:
                return shiftday.lunchShifts
            elif not lunch and len(shiftday.dinnerShifts)> 0:
                return shiftday.dinnerShifts
        return -1

    #Probably unused, delete
    def getNextAvailableShift(self):
        '''
            returns next available shiftday if one is available otherwise returns -1
        '''
        for i in range(1, self.numDays+1):
            shiftday = self.days[i]
            if shiftday.isDinnerFull() and shiftday.isLunchFull():
                continue
            elif shiftday.isLunchFull():
                return shiftday.dinnerShifts
            elif shiftday.isDinnerFull():
                return shiftday.lunchShifts
            else:
                return shiftday.dinnerShifts #if neither shifts are full then start with dinner shift        


    def assignShift(self, day, time, employee, lunch = False, replace=True):
        '''
            Assigns Employee to shift at time specified on day specified if that shift is available
            employee shoud be Employee class
            time should be a time class
            returns 1 if successful, -1 otherwise
        '''
        if day >= 1 and day <= self.numDays:
            day-=1
            shiftday = self.days[day]
            print("accessed self.days[%d]"%day)
            print(shiftday)
            match = shiftday.findShift(time, lunch)
            print("match:%s"%match)
            
            if replace or (not replace and match == None):
                print("found a shift")
                if lunch:
                    shiftday.setLunchShift(time, employee)
                else:
                    shiftday.setDinnerShift(time, employee)
            else:
                shiftday.printTimestamp(time, "Could not assign shift ")
                
        else:
            print("invalid day")
            return -1

    def assignShiftEveryWeek(self, weekday, time, employee, lunch = False, replace=True):
        if weekday in range(0,7):
            day = weekday - self.firstDay +1
            if day <= 0:
                day += 7
            print("first day:%d"%day)

            while day <= self.numDays:
                check = self.assignShift(day, time, employee, lunch, replace) #day+1: day is zero-indexed but assignShift takes day >=1 <=numDays
                if check == -1:
                    print("day %d failed"%day)
                    return -1 #day out of bounds.

                print("day %d succeeded"%day)
                day += 7
            return 1
        return -1

    def clearSingleShift(self, day, time, lunch=False):
        '''
            If time == None then clear all shifts for that day
        '''
        if day in range(1,self.numDays+1):
            shiftday = self.days[day-1]
            if time != None:
                if lunch:
                    shiftday.setLunchShift(time, None)
                else:
                    shiftday.setDinnerShift(time, None)
            else:
                if lunch: shiftday.clearLunch()
                else: shiftday.clearDinner()

    def clearShiftsEveryWeek(self, weekday, time, lunch=False):
        '''
            Sets specified shift (time) every weekday (0-6) to None (no employee working)
            If time == None then clear all shifts
        '''
        if weekday in range(0,7):
            day = weekday - self.firstDay +1
            if day <= 0:
                day += 7

            while day <= self.numDays:
                if time != None:
                    check = self.assignShift(day, time, None, lunch)
                    if check == -1:
                        return -1
                else:#clear all shifts
                    self.clearSingleShift(day, None, lunch)

                day += 7
            return 1
        return -1

    def clearAllShifts(self):
        '''
            Sets all shifts in calendar to None
        '''
        for d in self.days:
            d.clearLunch()
            d.clearDinner()

    def deleteSingleShift(self, day, time, lunch=False):
        '''
            Deletes a single shift
        '''
        if day in range(1,self.numDays+1):
            shiftday = self.days[day-1]
            if lunch:
                shiftday.removeLunchShift(time)
            else:
                shiftday.removeDinnerShift(time)
            return 1
        return -1

    def deleteShiftEveryWeek(self, weekday, time, lunch=False):
        '''
            Deletes a shift every weekday
        '''
        if weekday in range(0,7):
            day = weekday - self.firstDay +1
            if day <= 0:
                day += 7

            while day <= self.numDays:
                check = self.deleteSingleShift(day, time, lunch)
                if check == -1:
                    return -1
                day += 7
            return 1
        return -1

    def removeAllForEmp(self, emp):
        '''
            Removes all shifts assigned to an employee & sets them to None
            @params emp: Employee object
        '''
        for d in range(0, self.numDays):
            shiftDay = self.days[d]
            shifts = shiftDay.getEmpShifts(emp)
            if len(shifts) > 0:
                print("shifts for day %d: %s"%(d+1, shifts))
                for s in shifts:
                    if s[0] == LUNCH: shiftDay.setLunchShift(s[1], None)
                    else: shiftDay.setDinnerShift(s[1], None)             

    def printShifts(self, days=None):
        '''
            Prints each day and corresponding shifts
            @params days: a list of the day numbers to print shifts for, default is every day of the month
                          other possibilities are range(1,self.numDays, 7) => specific day of the week
                          or range(0,7) => a specific week.
        '''
        if days == None: days = range(1, self.numDays+1)
        anyShifts = False
        for i in days:
            shiftday = self.days[i-1]
            res = ""
            res+="  Lunch:"

            if len(shiftday.lunchShifts) != 0:
                res += "\n"
                res +="%s"%shiftday.printShift(True)
            else:
                res +="No Shifts Set."

            res +="\n  Dinner:"
            if len(shiftday.dinnerShifts) != 0:
                res += "\n"
                res +="%s"%shiftday.printShift(False)
            else:
                res += "No Shifts Set\n"

            if len(shiftday.lunchShifts) != 0 or len(shiftday.dinnerShifts) != 0:
                res = "%s %d:\n"%(DAY_NAMES[shiftday.weekday], i) + res
                anyShifts = True
                print(res)

        if anyShifts == False:
            print("No shifts to print.")

    
    def printCal(self, weeknums=False):
        '''prints daynumbers in calendar format'''
        weekdays_bar = "  M    T    W   Th    F   Sa   Su "
        weeknum = 1
        if weeknums:
            weekdays_bar = "   "+weekdays_bar
        print(weekdays_bar)
        for i in range(0, self.numDays+self.firstDay):
            if i<self.firstDay:
                print("     ", end="")
            else:
                if ((i-self.firstDay)+1) < 10:
                    print("  %d  "%((i-self.firstDay)+1), end="")
                else:
                    print(" %d  "%((i-self.firstDay)+1), end="")

            if i%7 == 6:
                print("")
        print("")

    def printWeekBounds(self):
        '''
            Prints daynum start and end of each week
        '''
        weeknum = 1
        firstDay = self.firstDay
        numWeeks = 5 if (self.numDays!= 28) else 4
        dayNum = 1
        while dayNum <= self.numDays:
            #start = firstDay
            if firstDay != 0: #not monday
                end = 7-firstDay
                firstDay = 0 #reset to start on monday
                #end_weekday = SOMETHING

            else:
                end = min(dayNum+6, self.numDays)
                #end_weekday = SOMETHING

            #TODO Add support for day names
            res = "Week %d: "%weeknum
            if dayNum%10 == 1:
                res += "%dst"%dayNum
            elif dayNum%10 == 2:
                res += "%dnd"%dayNum
            elif dayNum%10 == 3:
                res += "%drd"%dayNum
            else:
                res += "%dth"%dayNum

            #res += " ("+DAY_NAMES[start]+")"

            res += " to the "
            if end%10 == 1:
                res += "%dst"%end
            elif end%10 == 2:
                res += "%dnd"%end
            elif end%10 == 3:
                res += "%drd"%end
            else:
                res += "%dth"%end

            #res += " ("+DAY_NAMES[end_weekday]+")"

            print(res)

            dayNum = end +1
            weeknum += 1


    def printPretty(self, file, cellHeight = 5):
        '''prints pretty version of calendar to a file (unreadable in terminal)'''
        if cellHeight <=3:
            cellHeight = 4 #minimum cell height

        f = open(file, 'w')
        #print header
        header = "SCHEDULE FOR %s %d"%(MONTH_NAMES[self.month].upper(),self.year)
        padding = (22*7) - 14 - len(str(MONTH_NAMES[self.month])) - len(str(self.year))
        if padding%2 == 1:
            pad1 = padding//2
            pad2 = padding//2 +1
        else:
            pad1 = padding//2
            pad2 = padding//2

        header = (" "*pad1) + header + (" "*pad2) + "\n\n"
        f.write(header)

        #print weekday names
        f.write("|------ Monday ------||----- Tuesday ------||----- Wednesday ----||----- Thursday -----||------ Friday ------||----- Saturday -----||------ Sunday ------|\n")
        numWeeks = (self.numDays // 7)
        numWeeks += 1
        firstDay = self.firstDay
        dayNum = 0 - self.firstDay
        dayNum2 = 1- self.firstDay #DayNum printed in the corner of each day
        #i is the current "week" or row of the calendar
        for i in range(0, numWeeks):
            weekday = 0 - firstDay
            weekShifts = [] #list containing dictionaries
            weekShiftsTimes = [] #list contianing only times

            if(i == 0):
                firstDay = 0 #set first day of week to monday for subsequent weeks

            #Go through all 7 days of the week even if some are not part of the month
            for z in range(0,7): 
                    if dayNum<0: #Not part of the month
                        weekShifts.append({})
                        weekShiftsTimes.append([])

                    elif dayNum >= self.numDays: #past end of month
                        weekShifts.append({})
                        weekShiftsTimes.append([])

                    else:
                        shiftDay = self.days[dayNum]
                        print("weekday=%d"%weekday)
                        print("dayNum = %d"%dayNum)
                        print("i=%d"%i)
                        #combine into one dictionary
                        tmp = shiftDay.lunchShifts.copy()
                        tmp.update(shiftDay.dinnerShifts)
                        weekShifts.append(tmp)
                        weekShiftsTimes.append(list(shiftDay.lunchShifts)+list(shiftDay.dinnerShifts))
                    weekday += 1
                    dayNum += 1

            longestList = max([len(i) for i in weekShiftsTimes])

            #Sort each day's shifts by time
            for day in range(0, len(weekShiftsTimes)):
                weekShiftsTimes[day].sort()
                print("weekShiftsTimes[%d] = %s"%(day, str(weekShiftsTimes[day])))


            #Print Week.
            for rows in range(0,max(cellHeight,longestList+2)): #height of each cell
                print("Row num: %d"%rows)
                print("Cell height: %d"%max(cellHeight,longestList+2))

                for weekday in range(0,7):

                    #Leave one blank line in first row
                    if rows == 0:
                        print("DayNum2=%d"%dayNum2)
                        if (dayNum2) < 1 or (dayNum2) > self.numDays: #out of bound days
                            day = "|                    |"
                        else:
                            day = "| %d "%dayNum2
                            day += " "*(20-2-len(str(dayNum2)))
                            day += "|"
                        
                        f.write(day)
                        dayNum2 += 1

                    elif len(weekShiftsTimes[weekday]) == 0:
                        f.write("|                    |") #20 blank spaces
                    else:
                        if len(weekShiftsTimes[weekday]) <= (rows-1):
                            f.write("|                    |")
                        else:
                            # print("len(weekShiftsTimes)=%d"%len(weekShiftsTimes))
                            # print("len(weekShiftsTimes[weekday=%d])=%d"%(weekday,len(weekShiftsTimes[weekday])))
                            # print("rows=%d"%rows)
                            time = weekShiftsTimes[weekday][rows-1]
                            emp = weekShifts[weekday][time]
                            res = "|"
                            data = "%s : %s"%(time, emp)
                            padding = max(0, 22 - len(data) -2)

                            res += data
                            res += " "*padding
                            res += "|"
                            f.write(res)
                f.write("\n")
            f.write("|--------------------||--------------------||--------------------||--------------------||--------------------||--------------------||--------------------|\n")

        f.close()
        print("Successfully Wrote file")



if __name__ == "main":
    test = ShiftCalendar(4, 2014)
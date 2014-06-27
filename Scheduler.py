#Scheduler Class

import os
import sys
import pickle
from Time import Time
from ShiftCal import ShiftDay, ShiftCalendar
from Employee import Employee, Rule

class Scheduler:
    '''Shift Scheduler'''

    def __init__(self, month, year):
        assert type(month) == int and type(year) == int, 'month and year should be integers'
        assert month in range(1,13) and year >= 0, 'month or year out of bounds'
        
        self.cal = ShiftCalendar(month, year)
        
        self.year = year
        self.month = month
        self.numDays = self.cal.numDays
        self.firstDay = self.cal.firstDay #which weekday month starts on (0-6)


        self.employeeList = [] #list of employee objects

    def save(self, f, info = False):
        '''
            Saves Scheduler data using python's pickle module
            @params f: open file pointer in "wb" mode
            @params info: T/F whether to print additional info while saving.
            @return: 1 if successful, -1 if unsuccessfull.
        '''
        print("Saving Scheduler data...")
        pickle.dump(self.year, f)
        pickle.dump(self.month, f)
        pickle.dump(self.numDays, f)
        pickle.dump(self.firstDay, f)
        #NOTE: Cannot pickle employeeList, need to pickle each employee individually and then reconstruct list.
        if info: print("  Saved scheduler attributes")
        if info: print("  Checking employee list")

        #save length of employee list
        pickle.dump(len(self.employeeList), f)
        print("")
        #If not 0 then save each employee
        if len(self.employeeList) != 0:
            print("Saving Employee data...")
            print("  %d employees to save\n"%len(self.employeeList))
            for e in self.employeeList:
                if not e.save(f, info):
                    print("An error occured!")
                    return False
                print("")

        else:
            print("No employee data to save...")

        #save shiftCal
        print("")
        if self.cal.save(f, info):
            return True
        else:
            return False
        
    def load(self, f, info = False):
        '''
            Loads scheduler, shiftcal, & employees from filename
            @params f: an open file pointer in "rb" mode
            @params info: T/F whether to print detailed loading info
            @return: True if no errors occurred, False otherwise
        '''
        try:
            print("Loading Scheduler data...")
            self.year = pickle.load(f)
            if info: print("  Read year: %d"%self.year)
            self.month = pickle.load(f)
            if info: print("  Read month: %d"%self.month)
            self.numDays = pickle.load(f)
            if info: print("  Read number of days: %d"%self.numDays)
            self.firstDay = pickle.load(f)
            if info: print("  Read first day: %d"%self.firstDay)
            print("  Loaded scheduler attributes")
            if info: print("  Checking employee data")

            numEmps = pickle.load(f)
            if info: print("  Read num employees: %d"%numEmps)
            self.employeeList = []
            emp_dict = {}
            print("")
            if numEmps == 0:
                print("No Employee data to load...")   
            else:
                print("Loading Employees...")
                print("  %d employees to load\n"%numEmps)
                for i in range(0, numEmps):
                    emp = Employee("dummy", 1) #dummy employee who will be overwritten by loaded emp
                    if emp.load(f, info):
                        self.employeeList.append(emp)
                        emp_dict[emp.getName()] = emp
                    else:
                        return False
                    print("")

            print("")
            self.cal = ShiftCalendar(1,1970) #dummy shiftCal
            if self.cal.load(f, emp_dict, info):
                return True
            else:
                print("Error occured loading calendar...")
                return False

        except FileNotFoundError:
            print("Couldnt find scheduler data file...")
            return False

    def addEmployee(self, employee):
        '''
            Adds an employee to the scheduler
            @params employee: an employee object to be added
        '''
        if employee.__class__.__name__ == "Employee":
            self.employeeList.append(employee)
            print("Employee %s added."%employee.getName())

    def removeEmployee(self, employee):
        '''
            Removes an employee from the scheduler and deletes any shifts assigned to him/her
            @params employee: Employee obect to be removed
            @return: returns 1 on success, -1 for any type of error.
        '''
        if employee.__class__.__name__ == "Employee":
            #IMPROVE THIS TO DELETE ALL THAT EMPLOYEES SHIFTS & RETURN MORE INFO
            if employee in self.employeeList:
                self.cal.removeAllForEmp(employee)
                print("Employee %s removed."%employee.getName())
                self.employeeList.remove(employee)
                return 1
            else:
                print("%s employee does not exist"%employee.getName())
        return -1

    def createShiftW(self, weekdays, times, lunch=False):
        '''
            Creates shifts with given times for each weekday in weekdays
            @params weekdays: list of weekdays to create shifts for (0-6)
            @params times: list of Time objects, start time of each shift for each day
            @params lunch: boolean if you want to create a lunch shift or dinner shift (lunch=False)

            @return: 1 if successful, -1 otherwise
        '''
        if len(weekdays) > 0 and len(times) > 0:
            for day in weekdays:
                self.cal.setShiftsByDay(day, times, lunch)
            return 1
        return -1

    def createShiftD(self, days, times, lunch=False):
        '''
            Creates shifts with given times for each day in days
            @params days: list of days to create shifts for (1-31)
            @params times: list of Time objects, start time of each shift for each day
            @params lunch: boolean if you want to create a lunch shift or dinner shift (lunch=False)

            @return: 1 if successful, -1 otherwise
        '''
        if len(days) > 0 and len(times) > 0:
            for d in days:
                self.cal.setSingleDay(d, times, lunch)
            return 1
        return -1

    def delShiftW(self, weekdays, times, lunch=False):
        '''
            Deletes shifts with given times for each weekday in weekdays
            @params weekdays: list of weekdays to delete shifts for (0-6)
            @params times: list of Time objects, start time of each shift for each day
            @params lunch: boolean if referring to a lunch shift or dinner shift (lunch=False)

            @return: 1 if successful, -1 otherwise
        '''
        if len(weekdays) > 0 and len(times) > 0:
            for day in weekdays:
                for t in times:
                    self.cal.deleteShiftEveryWeek(day, t, lunch)
            return 1
        return -1

    def delShiftD(self, days, times, lunch = False):
        '''
            Deletes shifts with given times for each day in days
            @params days: list of days to delete shifts for (1-31)
            @params times: list of Time objects, start time of each shift for each day
            @params lunch: boolean if referring to a lunch shift or dinner shift (lunch=False)

            @return: 1 if successful, -1 otherwise
        '''
        if len(days) > 0 and len(times) > 0:
            for d in days:
                for t in times:
                    if self.cal.deleteSingleShift(d, t, lunch) == -1:
                        print("Failed to delete shift %d - %s"%(d, t))
                        return -1
            return 1
        else:
            return -1

    def assignW(self, emp, weekdays, times, lunch = False):
        '''
            Assigns employee to shifts with given times for each weekday in weekdays
            @params emp: Employee object assigned to each shift
            @params weekdays: list of weekdays to assign shifts for (0-6)
            @params times: list of Time objects, start time of each shift for each day
            @params lunch: boolean if referring to a lunch shift or dinner shift (lunch=False)

            @return: 1 if successful, -1 otherwise
        '''
        if emp.__class__.__name__=="Employee" and len(weekdays) > 0 and len(times) > 0:
            for d in weekdays:
                for t in times:
                    self.cal.assignShiftEveryWeek(d, t, emp, lunch)
            return 1
        return -1

    def assignD(self, emp, days, times, lunch=False):
        '''
            Assigns employee to shifts with given times for each day in days
            @params emp: Employee object assigned to each shift
            @params days: list of days to assign shifts for (1-31)
            @params times: list of Time objects, start time of each shift for each day
            @params lunch: boolean if referring to a lunch shift or dinner shift (lunch=False)

            @return: 1 if successful, -1 otherwise
        '''
        if emp.__class__.__name__=="Employee" and len(weekdays) > 0 and len(times) > 0:
            for d in days:
                for t in times:
                    self.cal.assignShift(d, t, emp, lunch)
            return 1
        return -1

    def clearW(self, weekdays, times="all", lunch=False):
        '''
            Clears shifts with given times for each weekday in weekdays
            @params weekdays: list of weekdays to clear shifts for (0-6)
            @params times: list of Time objects, start time of each shift for each day
                           can also be a string "all" indicating all shifts for those weekdays should be cleared
            @params lunch: boolean if referring to a lunch shift or dinner shift (lunch=False)

            @return: 1 if successful, -1 otherwise
        '''
        if len(weekdays) > 0 and len(times) > 0:
            if times == "all": times = [None] #more intuitive way to indicate clearing all shifts
            for day in weekdays:
                for t in times:
                    self.cal.clearShiftsEveryWeek(day, t, lunch)
            return 1        
        return -1

    def clearD(self, days, times="all", lunch=False):
        '''
            Clears shifts with given times for each day in days
            @params days: list of days to clear shifts for (1-31)
            @params times: list of Time objects, start time of each shift for each day
                           can also be a string "all" indicating all shifts for those days should be cleared
            @params lunch: boolean if referring to a lunch shift or dinner shift (lunch=False)

            @return: 1 if successful, -1 otherwise
        '''
        if len(days) > 0 and len(times) > 0:
            for d in days:
                for t in times:
                    self.cal.clearSingleShift(d, t, lunch)
            return 1
        return -1

    def matchShift(self, employee, l, t, wd, wn, d):
        '''
            Creates a rule from shift info provided and matches with given employee
            @params employee: Employee object
            @params d: integer (1-31) indicating day to match
            @params l: boolean indicating whether to match a lunch or dinner shift
            @params t: A string representing the time at which shift starts
            @params wd: integer (0-6) indicating which day of the week shift is on
            @params wn: integer (1-6) indicating which number week the shift is on

            @returns: True or False depending on whether employee can work that shift.
        '''
        if employee not in self.employeeList:
            print("Employee not found.")
            return -1

        shift_rule = Rule(lunch=l, time=t, weekday=wd, weeknum=wn, daynum=d)

        return employee.matchRule(shift_rule)

    def run(self, depth):
        '''
            Run scheduler until finding a complete schedule
            Should take into account priority & alternate between all employees equally
        '''
        #Clear previous assignments
        self.cal.clearAllShifts()
        print("\nAll shifts cleared")
        self.cal.printCal()
        print("")
        print(self.employeeList)
        res = self.assignEmployee(1, self.cal.getDay(1), self.employeeList.copy().sort(), depth)
        print("\nScheduling Done: %s"%res)
        return res

    def assignEmployee(self, daynum, shift_day, employeeList, depth=-1):
        '''
            Recursive function, on each call tries to assign employee from employeeList to an open shift in shift_day
            Then removes employee assigned from employeeList and calls itself until day is filled.
            If employeeList empty and day not complete, declare failure
            Else if day is complete, rebuild employee list and call recursively on next day
            If daynum > number of days in month, check if calendar is complete, else return failure.

            @params daynum: integer (1 to numDays in month), day we are working on
            @shift_day: ShiftDay object of that day
            @employeeList: list of employees ordered by priority
            @depth: integer indicating how many recursive calls to execute before stopping, used for testing. -1 disables limiting depth

            @return: True if found a complete schedule, False if not. Modifies the shiftcalendar in place
        '''
        #No more shifts left to schedule
        if self.cal.isComplete():
            return True

        #We are done with all days
        if daynum > self.cal.numDays:
            return self.cal.isComplete()

        #Stop scheduling for testing purposes
        if depth == 0:
            return True

        print("Trying to schedule day %d"%daynum)

        shift = shift_day.getNextEmptyShift()

        #No more shifts left for this day, move on to next day
        if shift == None:
            print("No more shifts left for this day.")
            empList = self.employeeList.copy() #get fresh employee list
            empList.sort()
            sd = self.cal.getDay(daynum+1)
            print("reset emp list to %s"%(str(empList)))
            return self.assignEmployee(daynum+1, sd, empList, depth)

        #Else there is a shift to schedule
        lunch = shift[0]
        time = shift[1]
        weekday = shift_day.weekday
        weeknum = shift_day.weeknum

        print("empList: %s"%(str(employeeList)))

        for e in employeeList:
            print("---------")
            print("Trying employee %s"%(str(e)))
            if self.matchShift(e, lunch, time, weekday, weeknum, daynum): #true if employee can work shift
                print("%s can work that shift!"%(str(e)))
                temp = e
                if lunch:
                    shift_day.setLunchShift(time, e)
                else:
                    shift_day.setDinnerShift(time, e)

                newEmpList = employeeList.copy()
                newEmpList.remove(e)
                print("new emp list: %s"%(newEmpList))
                print("new depth = %d"%(depth-1))

                if not self.assignEmployee(daynum, shift_day, newEmpList, depth-1):
                    #scheduling was unsuccessful, undo assignment
                    if lunch:
                        shift_day.setLunchShift(time, None)
                    else:
                        shift_day.setDinnerShift(time, None)
                    continue #next employee
                else: 
                    #everything went well
                    return True
        #We get here if we have gone through all employees so declare failure
        return False
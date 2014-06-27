#Scheduler UI Class
#Handles all the UI and input for the scheduler

import os
import sys
import pickle
from Time import Time
from ShiftCal import ShiftDay, ShiftCalendar
from Employee import Employee, Rule
from Scheduler import Scheduler


class Scheduler_UI:
    '''
        UI for Scheduler, user-friendly way to enter shifts, employees and create a schedule
    '''
    
    def __init__(self, month=None, year=None, debug=False, name="Evan's"):
        self.monthNames = ["Dummy", "January","February","March","April","May","June","July","August","September","October","November","December"]
        self.weekdayAbbr = {"m":0, "t":1, "w":2, "th":3, "f":4, "s":5, "su":6}
        self.schedName = name
        self.curEmployee = None #the employee whose page you are at
        self.month = month
        self.year = year
        self.employeeNames = {}
        self.ver = "0.9" #bumped after getting working scheduler
        
        self.__start(month, year)
        if not debug:
            self.__mainLoop()
        else:
            print("DEBUG MODE")

    def __start(self, month=None, year=None):
        '''
            Does basic configuration from user input
        '''
        if (month == None or year == None) or (month not in range(1,13) and year <= 0):
            self.printTitle()
            print("Let's get started by filling out some basic information:")
            self.year = self.getInputOfType("Enter the current year: ", 'int', range(0,2500))
            self.month = self.getInputOfType("Enter the current month (numeric): ", 'int', range(1,13))

        self.scheduler = Scheduler(self.month, self.year)

        name = self.getInputOfType("[Optional] Enter name of your restaurant: ", "str", range(0,20), True)
        if name != "skip":
            self.schedName = name
        
        self.printTitle()
        print("Scheduler configured for %s %s"%(self.monthNames[self.month], self.year))
        print("")
        print("Here is an overview of the month:")
        self.printCalendar()
        print("")
        print("You should start by adding Employees and then specifying availability/rules for each employee. " +
            "Then set shifts for each day/week of the month.")
        print("")
        print("Type help at any time for help using this app.\n")


    def __mainLoop(self):
        '''
            main loop for the UI
        '''
        while True:
            print("")
            case_command = input(">>>")
            command = case_command.lower()
            if command == "help" or command == "h":
                self.printHelp()

            elif command == "employees" or command == "emps":
                self.printEmployees()

            elif command == "add employee" or command == "add emp" or command == "new employee" or command == "new emp":
                self.addEmployee()

            elif command == "quit" or command == "q":
                print("You will lose any unsaved changes.")
                if self.getInputOfType("Are you sure you want to quit? (y/n)", "bool"):
                    print("Exiting...")
                    sys.exit(0)

            elif command == "about":
                self.printAbout()

            elif len(command) > 5 and command[0:5] == "save ":
                if len(command) > 8 and command[5:7] == "-v":
                    filename = case_command[7:]
                    self.save(filename, True)
                else:
                    filename = case_command[5:]
                    self.save(filename)

            elif len(command) > 5 and command[0:5] == "load ":
                if len(command) > 8 and command[5:7] == "-v":
                    filename = case_command[7:]
                    self.load(filename, True)
                else:
                    filename = case_command[5:]
                    self.load(filename)

            elif command == "run" or command == "r":
                #run scheduler
                depth = self.getInputOfType("How many iterations? ", "int", range(-1, 9999999))
                self.scheduler.run(depth)

            elif command == "shifts" or command == "ps":
                self.scheduler.cal.printShifts()

            elif command == "edit shifts" or command == "edit s":
                self.editShifts()

            elif len(command) > 13 and command[:10] == "print cal ":
                out_file = case_command[10:]
                self.printCal(out_file)

            #Type employee name to access their page
            elif case_command in self.employeeNames.keys():
                self.configEmployee(self.employeeNames[case_command])

            #delete employee
            elif len(command) > 4 and command[:4] == "del ":
                employeeName = case_command[4:]
                if employeeName in self.employeeNames.keys():
                    self.delEmployee(self.employeeNames[employeeName])
                else:
                    print("Employee '%s' not recognized."%employeeName)

            else:
                self.cmdNotRecognized(command)


    def save(self, filename, info = False):
        '''
            Saves all objects to 'filename'
            @params filename: a String.
            @params info: T/F whether to print additional info while saving.
        '''
        if len(filename) > 0 and filename not in [" ", ",", "/","\\"]:
            ui_f = filename+".esf"
            if os.path.isfile(ui_f):
                print("Found existing save %s, are you sure you want to overwrite it?"%filename)
                if not self.getInputOfType("(Y/N) : ", "bool"):
                    print("Cancelling save...")
                    return
                else:
                    os.remove(ui_f)
                    print("File deleted...")

            f = open(ui_f, "wb")
            if info: print("Created save file: %s.\n"%ui_f)
            print("Saving Scheduler UI data...")
            #Don't need to save curEmployee since can only save from main screen => curEmp = None
            #Reconstruct employeeNames dict from employee list in sched
            pickle.dump(self.ver, f) #save version number
            if info: print("  Saved version number")
            pickle.dump(self.schedName, f) #save custom schedule name
            if info: print("  Saved restaurant name")
            print("")
            if self.scheduler.save(f, info): #also performs save
                f.close()
                print("Save successful for %s"%filename)
                input("\nPress Enter to continue...")
                self.toMainScreen()
            else:
                f.close()
                print("Save %s failed."%filename)
        else:
            print("Error: Invalid save name %s..."%filename)

    def load(self, filename, info=False):
        '''
            Loads all objects from 'filename'
            @params filename: a String
            @params info: T/F whether to display additional info while loading
        '''
        if len(filename) > 0 and filename not in [" ", ",", "/","\\"]:
            ui_f = filename+".esf"
            #Check & Open file
            try:
                f = open(ui_f, "rb")
                if info: print("\nFound save file %s\n"%ui_f)
            except FileNotFoundError:
                print("Error: Couldn't find required file %s"%ui_f)
                return

            try:
                print("Loading Scheduler UI data...")
                candidate_ver = pickle.load(f)
                if info: print("  Read version number: %s"%candidate_ver)

                #Version check
                if candidate_ver != self.ver:
                    print("\nWarning: Saved schedule is an older version (v.%s) than the scheduler (v.%s)."%(candidate_ver, self.ver))
                    print("Warning: There may be unexpected problems when loading this file.")
                    if not self.getInputOfType("Are you sure you want to continue loading? (y/n) : ", "bool"): return
                    print("\nResuming load...")

                self.schedName = pickle.load(f)
                if info: print("  Read restaurant name: %s"%self.schedName)
            except Exception as e:
                print("\nError: %s\n"%str(e))
                raise e
                return

            #Move on to scheduler
            print("")
            if self.scheduler.load(f, info):
                print("")
                print("Finishing up...")
                self.month = self.scheduler.month
                self.year = self.scheduler.year
                if info: print("  Loaded calendar attributes from scheduler...")
                self.curEmployee = None #should be None anyways.
                self.employeeNames = {}
                for e in self.scheduler.employeeList:
                    self.employeeNames[e.getName()] = e
                if info: print("  Rebuilt employee mapping...")
                f.close()
                print("\nLoad successful!\n")
                input("\nPress Enter to continue...")
                self.toMainScreen()
            else:
                print("Load failed, some data may have been overwritten. Please restart the scheduler.")
                f.close()
                #change this to rollback
        else:
            print("Invalid save name %s..."%filename)

    def editShifts(self):
        '''
            Edit Shifts screen allows viewing all shifts, adding shifts by day, week, or more.
        '''
        self.printTitle("Add and Edit Shifts")
        self.printCalendar(True)
        print("")

        while True:
            print("")
            case_command = input(">>>")
            command = case_command.lower()

            if command == "back" or command == "b":
                self.toMainScreen()
                break

            elif command == "quit" or command == "q":
                print("You will lose any unsaved changes.")
                if self.getInputOfType("Are you sure you want to quit? (y/n)", "bool"):
                    print("Exiting...")
                    sys.exit(0)

            elif command == "help" or command == "h":
                self.printHelp("shift")

            elif len(command) > 10 and command[:9] == "print cal":
                out_file = case_command[10:]
                self.printCal(out_file)

            elif command == "shifts" or command == "ps" or command == "print shifts":
                self.scheduler.cal.printShifts()

            elif command == "week bounds" or command == "wb":
                self.scheduler.cal.printWeekBounds()

            elif len(command) > 5 and command[:5] == "week ":
                try:
                    weeknum = int(command[5])
                except:
                    print("usage: week #")

                if weeknum > 6 or weeknum <= 0:
                    print("Week number is out of bounds.")
                    continue

                #set up range of daynums for given week
                firstD = self.scheduler.cal.firstDay
                if weeknum == 1:
                    self.scheduler.cal.printShifts(range(1, 7-firstD+1))
                else:
                    start = (weeknum-2)*7 +(7-firstD+1)
                    self.scheduler.cal.printShifts(range(start, start+7))

            elif command in self.weekdayAbbr.keys() or command in ["mondays", "tuesdays", "wednesdays", "thursdays", "fridays", "saturdays", "sundays"]:
                if command == "thursdays" or command == "sundays":
                    weekday = self.weekdayAbbr[command[0:2]]
                else:
                    weekday = self.weekdayAbbr[command[0]]

                firstD = self.scheduler.cal.firstDay
                start = weekday - firstD + 1
                if start <= 0: start += 7
                self.scheduler.cal.printShifts(range(start, self.scheduler.numDays+1, 7))

            elif len(command) > 4 and command[:4] == "day ":
                try:
                    daynum = int(command[4:6])
                except:
                    try:
                        daynum = int(command[4])
                    except:
                        print("usage: day #")

                if daynum <= 0 or daynum > self.scheduler.cal.numDays:
                    print("Day number out of bounds.")
                    continue

                self.scheduler.cal.printShifts([daynum])

            elif command == "employees" or command == "emps":
                self.printEmployees()

            elif command == "add employee" or command == "add emp" or command == "new emp" or command =="new employee":
                print("You must add an employee from the main screen. Return to the main screen with the 'back' command.")

            elif command == "set weekday" or command == "set w":
                weekdays = self.getInputOfType("Create shifts for which weekday(s)? (M,T,W,Th,F,S,Su) : ", "str", range(1,3))
                if weekdays == "cancel": continue
                print("")
                lunch = self.getLunch()
                if lunch == "cancel": continue
                print("")
                times = self.getTimes()
                if times == "cancel": continue
                    
                #times is guaranteed to have atleast 1 elem
                if type(weekdays) != list:
                    weekdays = [weekdays] #enforce list format

                weekdaysAsNum = []
                for wd in weekdays:
                    weekdaysAsNum.append(self.weekdayAbbr[wd.lower()])
                
                res = self.scheduler.createShiftW(weekdaysAsNum, times, lunch)
                if res == 1:
                    print("Shifts successfully added for %s."%weekdays)
                else:
                    print("No shifts created.")  

            elif command == "set day" or command == "set d":
                days = self.getInputOfType("Create shifts for which day(s)? : ", "int", range(1, self.scheduler.numDays+1))
                if days == "cancel": continue
                print("")
                lunch = self.getLunch()
                if lunch == "cancel": continue
                #enter times
                print("")
                times = self.getTimes()
                if times == "cancel": continue
                
                if type(days) != list:
                    days = [days]

                if self.scheduler.createShiftD(days, times, lunch) == 1:
                    print("Successfully created shift on the %s."%days)
                else:
                    print("No shifts created.")

            elif command == "del weekday" or command == "del w":
                weekdays = self.getInputOfType("Delete shifts for which weekday(s)? (M,T,W,Th,F,S,Su) : ", "str", range(1,3))
                if weekdays == "cancel": continue
                print("")
                lunch = self.getLunch()
                if lunch == "cancel": continue
                print("")
                times = self.getTimes()
                if times == "cancel": continue

                if type(weekdays) != list:
                    weekdays = [weekdays]

                weekdaysAsNum = []
                for wd in weekdays:
                    weekdaysAsNum.append(self.weekdayAbbr[wd.lower()])

                if self.scheduler.delShiftW(weekdaysAsNum, times, lunch) == 1:
                    print("Successfully deleted shifts on %s at %s."%(weekdays, times)) 
                else:
                    print("Operation failed.")

            elif command == "del day" or command == "del d":
                days = self.getInputOfType("Delete shifts for which day(s)? : ", "int", range(1, self.scheduler.numDays+1))
                if days == "cancel": continue
                print("")
                lunch = self.getLunch()
                if lunch == "cancel": continue
                print("")
                times = self.getTimes()
                if times == "cancel": continue
                
                if type(days) != list:
                    days = [days]
                
                if self.scheduler.delShiftD(days, times, lunch) == 1:
                    print("Successfully deleted shifts on %s at %s."%(days, times))
                else:
                    print("Operation failed.")

            elif command == "assign weekday" or command == "assign w":
                weekdays = self.getInputOfType("Assign shifts for which weekday(s)? (M,T,W,Th,F,S,Su) : ", "str", range(1,3))
                if weekdays == "cancel": continue
                print("")
                lunch = self.getLunch()
                if lunch == "cancel": continue
                print("")
                emp = self.getEmpName()
                if emp == "cancel": continue
                print("")
                times = self.getTimes()
                if type(weekdays) != list:
                    weekdays = [weekdays]

                weekdayAsNum = []
                for day in weekdays:
                    weekdayAsNum.append(self.weekdayAbbr[day.lower()])
                        
                if self.scheduler.assignW(emp, weekdayAsNum, times, lunch) == 1:
                    print("Successfully assigned %s to shifts %s on %s."%(emp.getName(),times, weekdays))
                else:
                    print("Shifts not assigned.")

            elif command == "assign day" or command == "assign d":
                days = self.getInputOfType("Assign shifts for which day(s)? : ", "int", range(1, self.scheduler.numDays+1))
                if days == "cancel": continue
                print("")
                lunch = self.getLunch()
                if lunch == "cancel": continue
                print("")
                emp = self.getEmpName()
                if emp == "cancel": continue
                print("")
                times = self.getTimes()
                if times == "cancel": continue

                if type(days) != list:
                    days = [days]
                    
                if self.assignD(emp, days, times, lunch) == 1:
                    print("Successfully assigned %s to shifts %s on %s."%(emp.getName(),times, days))
                else:
                    print("Shifts not assigned.")

            elif command == "clear weekday" or command == "clr w":
                weekdays = self.getInputOfType("Clear a shift for which weekday(s)? (M,T,W,Th,F,S,Su) : ", "str", range(1,3))
                if weekdays == "cancel": continue
                print("")
                lunch = self.getLunch()
                if lunch == "cancel": continue
                allShifts = self.getInputOfType("Would you like to clear all shifts? (y/n) :", "bool")
                if allShifts == "cancel": continue
                print("")
                if not allShifts:
                    times = self.getTimes()
                    if times == "cancel": continue
                else:
                    times = "all"

                if type(weekdays) != list:
                    weekdays = [weekdays]
                
                weekdayAsNum = []
                for d in weekdays:
                    weekdayAsNum.append(self.weekdayAbbr[day.lower()])

                if self.scheduler.clearW(weekdayAsNum, times, lunch) == 1:
                    print("Successfully cleared shifts %s on %s."%(times, weekdays))
                else:
                    print("Shifts not cleared.")

            elif command == "clear day" or command == "clr d":
                days = self.getInputOfType("Clear a shift for which day(s)? : ", "int", range(1, self.scheduler.numDays+1))
                if days == "cancel": continue
                print("")
                lunch = self.getLunch()
                if lunch == "cancel": continue
                print("")
                allShifts = self.getInputOfType("Would you like to clear all shifts? (y/n) :", "bool")
                if allShifts == "cancel": continue
                print("")
                if not allShifts:
                    times = self.getTimes()
                    if times == "cancel": continue
                else:
                    times = "all"

                if type(days) != list:
                    days = [days]

                if self.scheduler.clearD(days, times, lunch) == 1:
                    print("Successfully cleared shifts %s on %s."%(times, days))
                else:
                    print("Shifts not cleared.")

            else:
                self.cmdNotRecognized(command)

    def getLunch(self):
        while True:
            lunch = self.getInputOfType("Is this a lunch or dinner shift? : ", "str", [5,6])
            if lunch == "lunch":
                return True
                
            elif lunch == "dinner":
                return False

            elif lunch == "cancel":
                return "cancel"
                
            else:
                print("Please enter either 'lunch' or 'dinner'.")

    def getTimes(self):
        print("You will now be prompted to enter times at which each shift will begin, you can enter as many as you like. " +
                    "\nTo stop entering times, enter 'stop' or 's'.")
        times = []
        tmp = self.getInputOfType("Enter a time : ", "time") #get first input
        if tmp == "cancel": return tmp #propagate "cancel" out to be handled later

        while tmp != "skip":
            times.append(tmp)
            tmp = self.getInputOfType("Enter a time : ", "time", None, True)
            if tmp == "cancel": return tmp
        return times

    def getEmpName(self):
        self.printEmployees()
        while True:
            inp = self.getInputOfType("Enter the name of an employee: ", "str", range(1, 20))
            if inp == "cancel": return "cancel"
            closest = ""
            for name in self.employeeNames.keys():
                if inp == name:
                    return self.employeeNames[name]
                elif inp in name:
                    closest = name
            if len(closest) != 0:
                print("Employee %s not found, did you mean %s?"%(inp,name))
            else:
                print("Employee %s not found."%inp)

    def printCal(self, out_file):
        if len(out_file) > 4 and out_file[-4:] == ".txt":
            self.scheduler.cal.printPretty(out_file)
            print("Calendar outputed to %s"%out_file)
        else:
            print("Output file must be a .txt file")


    def delEmployee(self, employee):
        emp_name = employee.getName()
        x = self.getInputOfType("Are you sure you want to delete employee %s? (y/n) : "%emp_name, "bool")
        if x:
            x = self.scheduler.removeEmployee(employee)
            del(self.employeeNames[emp_name])
            print("Successfully deleted employee %s."%employee.getName())
        else:
            print("Employee not deleted.")

    def addEmployee(self):
        '''
            Interface to add an employee and configure him/her
        '''
        self.printTitle("Add Employee")
        #Added check to prevent duplicate employee names
        while True:
            name = self.getInputOfType("Enter a name for new employee: ", "str", range(1,20)) #20 chars max
            if name not in self.employeeNames:
                break
            print("Name '%s' already taken!"%name)

        if name != "cancel":
            priority = self.getInputOfType("Enter employee priority: ", "int", range(0,1000)) #priority must be non negative
            
            if priority != "cancel":
                new_emp = Employee(name, priority)
                self.scheduler.addEmployee(new_emp)
                self.employeeNames[new_emp.getName()] = new_emp
                print("...")
                print("Successfuly created employee %s"%new_emp.getName())
                cont = self.getInputOfType("Would you like to configure employee now? (y/n): ", "bool")

                if cont:
                    self.configEmployee(new_emp)
                else:
                    self.toMainScreen()
                    #returns to main screen
            else:
                self.toMainScreen()
        else:
            self.toMainScreen()


    def configEmployee(self, employee):
        '''
            Configures an already existing employee.
            employee var must be instance of Employee
        '''
        if employee.__class__.__name__ != "Employee":
            print("employee parameter of configEmployee is not an employee object!")

        self.curEmployee = employee

        windowTitle = "Edit Employee Page for %s\nPriority : %d"%(employee.getName(), employee.getPriority())
        self.printTitle(windowTitle)
        print("Current Configured Rules:")

        employee.printRules()

        while True:
            print("")
            case_command = input(">>>")
            command = case_command.lower()

            if command == "quit" or command == "q":
                print("You will lose any unsaved changes.")
                if self.getInputOfType("Are you sure you want to quit? (y/n)", "bool"):
                    print("Exiting...")
                    sys.exit(0)

            elif command == "back" or command =="b":
                self.toMainScreen()
                break #return to mainloop

            elif command == "help" or command == "h":
                self.printHelp("emp")

            elif command == "new rule" or command =="new":
                print("Creating Rule %d"%(len(self.curEmployee.rules)+1))
                params = {}
                lunch = self.getInputOfType("Available for lunch? (y/n) : ", "bool")
                if lunch == "cancel": continue
                elif lunch != False:
                    dinner = self.getInputOfType("Available for dinner? (y/n) : ", "bool")
                    if dinner == "cancel": continue
                else: #if lunch is false then must be a dinner shift
                    dinner = True
                    print("Scheduling a dinner shift...")

                #lunch = T, dinner = F
                if not lunch and dinner:
                    params["lunch"] = False
                elif lunch and not dinner:
                    params["lunch"] = True
                #else default to available for both (lunch = T & dinner = T) or (lunch = F & dinner = F)
                           
                print("")
                print("You can skip some of the next questions by typing 'skip' or 's'...")
                print("You can also enter a list for each field by separating each value with a comma.\n")
                self.printCalendar(True, True) #print with header and weeknums

                days = self.getInputOfType("[optional] Day(s) Available : ", "int", range(1,self.scheduler.numDays+1), True) #skippable = True
                if days == "cancel": continue

                if days != "skip":
                    params["daynum"]=days
                    #Dont need other fields except time

                else:
                    #get atleast one of weekday or weeknum and get time
                    weekdays = self.getInputOfType("[optional] Weekdays Available? (M,T,W,Th,F,S,Su) : ", "str", range(1,3), True) #is skippable
                    if weekdays == "cancel": continue

                    elif weekdays == "skip":
                        print("")
                        print("Select week(s) by number:")
                        weeknums = self.getInputOfType("[required] Which Weeks Available? (ex: 1,2,4) : ", "int", range(1,5))
                        if weeknums == "cancel": continue

                        params["weeknum"] = weeknums
                        #Finish

                    else:
                        #translate to nums
                        weekday_nums = []
                        for day in weekdays:
                            if day.lower() in self.weekdayAbbr.keys():
                                weekday_nums.append(self.weekdayAbbr[day.lower()])
                            else:
                                print("%s is not a valid day, aborting..."%day)
                                continue

                        if len(weekday_nums) > 0:  
                            weekday_nums.sort() #put days in order      
                            params["weekday"] = weekday_nums

                        #optional weeknums
                        self.scheduler.cal.printWeekBounds()
                        weeknums = self.getInputOfType("[optional] Which Weeks Available? (ex: 1,2,4) : ","int",range(1,5), True)
                        if weeknums == "cancel": continue

                        if weeknums != "skip":
                            params["weeknum"] = weeknums

                #create rule
                if len(params) != 0:
                    #get time
                    t = self.getInputOfType("[required] Available after? (24hour or 12hour w/ pm) : ", "time", range(3,9))
                    if t == "cancel": continue
                    params["time"] = t
                    
                    r = Rule(**params)
                    self.curEmployee.setRule(r)

                    #Refresh employee page
                    self.printEmpPage(self.curEmployee, "Successfully created rule %d"%len(self.curEmployee.rules))

                else:
                    print("Something went wrong... params=%s"%params)

            elif command == "set maxshifts" or command =="set ms":
                num = self.getInputOfType("Enter maximum number of shifts for the month: ", "int", range(0, (self.scheduler.numDays+1)*2))
                if num == "cancel": continue
                print("...")
                r = Rule(maxshifts=num)
                
                for rule in self.curEmployee.getRules():
                    if rule.hasKey("maxshifts"):
                        self.curEmployee.deleteRule(rule) #overwrite any previous max shift rule
                        print("Deleted old max shifts value")

                self.curEmployee.setRule(r)
                #Refresh employee page
                self.printEmpPage(self.curEmployee, "Successfully set new max shifts value.")

            elif command == "set maxshiftsperweek" or command == "set mspw":
                num = self.getInputOfType("Enter maximum number of shifts allowed per week: ", "int", range(0, 14))
                if num == "cancel": continue
                print("...")
                r = Rule(maxshiftsPW=num)
                
                for rule in self.curEmployee.rules:
                    if rule.hasKey("maxshiftspw"):
                        self.curEmployee.deleteRule(rule) #overwrite any previous max shift rule
                        print("Deleted old max shifts per week value")

                self.curEmployee.setRule(r)
                #Refresh Employee page
                self.printEmpPage(self.curEmployee, "Successfully set new max shifts per week value.")

            elif command == "del rule" or command == "del":
                self.curEmployee.printRules()
                print("Select rule by number")
                r = self.getInputOfType("Rule number: ", "int", range(1,len(self.curEmployee.rules)+1))
                if r == "cancel": continue

                rule = self.curEmployee.getRule(r-1)
                self.curEmployee.deleteRule(rule)
                print("...")
                self.printEmpPage(self.curEmployee, "Rule %d successfully deleted"%r)


            elif command == "change priority" or command == "chg p":
                new_p = self.getInputOfType("Enter new priority: ", "int", range(0,100))
                if new_p == "cancel": continue
                self.curEmployee.chgPriority(new_p)
                #Refresh employee page
                self.printEmpPage(self.curEmployee, "Successfully changed priority.")

            elif command == "change name" or command == "chg n":
                if self.curEmployee == None:
                    print("Incorrect Employee Pointer")
                    sys.exit(0)

                ##Added check to prevent duplicate employee names
                while True:
                    new_name = self.getInputOfType("Enter new name: ", "str", range(1,20))
                    if new_name not in self.employeeNames:
                        break
                    print("Name '%s' already taken!"%new_name)
                if new_name == "cancel": continue

                old_name = self.curEmployee.getName()
                self.employeeNames[new_name] = self.curEmployee
                del(self.employeeNames[old_name])
                self.curEmployee.name = new_name

                #Refresh employee page
                self.printEmpPage(self.curEmployee, "Name successfully changed.")

            elif command == "exclude" or command == "ex":
                days = self.getInputOfType("Which days should be excluded? ", "int", range(0,(self.scheduler.numDays+1)))
                if days == "cancel": continue

                print("...")
                r = Rule(exclude = days)

                self.curEmployee.setRule(r)
                #Refresh employee page
                self.printEmpPage(self.curEmployee, "Successfully created exclude rule.")

            else:
                self.cmdNotRecognized(command)

        self.curEmployee = None
        #return to _mainloop()

    def printEmpPage(self, emp, opMsg = ""):
        '''
            Print the Employee configuration page header & optional operation epilogue message
            @params emp: employee being configured
            @params opMsg: String displayed after header specifying operation result
        '''
        windowTitle = "Edit Employee Page for %s\nPriority : %d"%(emp.getName(), emp.getPriority())
        self.printTitle(windowTitle)
        emp.printRules()
        print(opMsg)

    def printEmployees(self):
        if len(self.scheduler.employeeList) == 0:
            print("No employees. Add one with the command 'add employee'")
        else:
            print("%d Employees"%len(self.scheduler.employeeList))
            for emp in self.scheduler.employeeList:
                print("\t%s : %d shifts"%(emp.getName(), emp.curNumShifts()))
            print("")

    def toMainScreen(self):
        self.printTitle("Month Overview") #print title of main screen
        self.printCalendar(True)
        print("")

    def printCalendar(self, header=False, weeknums = False):
        if header:
            m_y = "%s %s"%(self.monthNames[self.month], self.year)
            space = 34 - len(m_y)
            s1 = int(space/2)
            s2 = int(space/2)
            if space%2 == 1:
                s2 += 1
            res = " "*s1
            res += m_y
            res += " "*s2
            res += "\n"
            print(res)
            
        self.scheduler.cal.printCal(weeknums)

    def printHelp(self, window="main"):
        '''
            Prints help using the app including available commands
            Prints commands specific to which window user is in ie 'main' is main window, 'emp' is the employee configuration window...
        '''
        curPage = "Month Overview"
        if window == "emp":
            curPage = "Edit Employee page for %s"%self.curEmployee.getName()
        elif window == "shift":
            curPage = "Edit Shifts Page"

        print("Current Page Description: %s"%curPage)
        print("Here are the available commands...")

        commands = ""

        if window == "main":
            commands += "Employees:\n"
            commands += "\t-employees : prints all the current employees.\n"
            commands += "\t-add employee : create a new employee.\n"
            commands += "\t-del 'employee_name': deletes employee with that name.\n"
            commands += "\t-'employee_name': edit that employee.\n"
            
            commands += "\nShifts:\n"      
            commands += "\t-edit shifts : brings you to the the edit shifts screen.\n"
            commands += "\t-shifts : prints all of the current shifts for each day.\n"
            
            commands += "\nOutput:\n" 
            commands += "\t-print cal 'file.txt': writes a calendar containing all shifts to file.\n"
            
            commands += "\nConfig & Run Scheduler:\n" 
            #commands += "\t-config : set settings related to algorithm that schedules shifts.\n"
            commands += "\t-run : run scheduler.\n"

            commands += "\nSave & Load:\n" 
            commands += "\t-save ['filename'] : save all data to file, default saves to 'autosave.esf' & overwrites existing file.\n"
            commands += "\t-load ['filename'] : loads from 'filename.esf'. By default looks for 'autosave.esf'.\n"            


        elif window == "emp":
            commands += "\t-back : return to month overview page.\n"

            commands += "\n"
            commands += "\t-new rule : create a new rule.\n"
            commands += "\t-del rule : delete a rule.\n"

            commands += "\n"
            commands += "\t-set maxshifts : set max number of shifts employee can work in a month.\n"
            commands += "\t-set maxshiftsperweek : set max number of shifts employee can work a week.\n"
            commands += "\t-exclude : exclude specific days from availability.\n"

            commands += "\n"
            commands += "\t-change name : change Employee name.\n"
            commands += "\t-change priority : change algorithm priority.\n"

        elif window == "shift":
            commands += "\t-back : return to month overview page.\n"

            commands += "\n"
            commands += "\t-shifts : print all shifts.\n"
            commands += "\t-employees : list all employees.\n"
            commands += "\t-week bounds : print the start and end dates of each week.\n"
            commands += "\t-week [num] : print shifts for given week.\n"
            commands += "\t-day [num] : print shifts for given day.\n"
            commands += "\t-[weekday] : print shifts for given weekday\n"
            commands += "\n"
            commands += "\t-set weekday : creates shift every weekday(s) of the month.\n"
            commands += "\t-set day : creates shift for specified day(s).\n"
            commands += "\n"
            commands += "\t-del weekday : deletes shift every weekday(s) of the month.\n"
            commands += "\t-del day : deletes shift every weekday(s) of the month.\n"
            commands += "\n"
            commands += "\t-clear weekday : clear shift every weekday(s) of the month.\n"
            commands += "\t-clear day : clear shift every weekday(s) of the month.\n"
            commands += "\n"
            commands += "\t-assign weekday : deletes shift every weekday(s) of the month.\n"
            commands += "\t-assign day : deletes shift every weekday(s) of the month.\n"            
            pass

        commands += "\nGeneral Commands:\n"
        commands += "\t-quit : quits program.\n"
        commands += "\t-help : displays available commands depending on screen.\n"
        print(commands)

        
    def printTitle(self, windowTitle="config"):
        '''
            Clears terminal window and prints info about App
        '''
        os.system("cls")
        title = "Welcome to %s Shift Scheduler v%s"%(self.schedName, self.ver)
        stars = "*"*len(title)
        print(title)
        print(stars)
        if windowTitle != "config":
            print(windowTitle)
        print("")

    def printAbout(self):
        '''
            Prints info about app and version number
        '''
        self.printTitle("About this program")
        print("Created by Evan Fossier. Summer 2014.")
        x = input("Press any key to go back") #display until user presses a key
        self.toMainScreen()

    def getInputOfType(self, prompt, type, range=False, skippable=False):
        '''
            Provides loop to get an input value that fits provided type (supports int, string, boolean) and optionally range(for int, range of length for string)
            @params prompt: string that will be displayed before input
            @params type: one of "int", "str", "bool", "time" specifying which type of input to look for
            @params range: list of acceptable inputs. For type "str" this specifies the allowed length of the input. Has no effect for "bool" and "time"
            @params skippable: True/False if user is allowed to skip this prompt
            
            @return : Input of type specified in type, if skippable, may return "skip", if user cancels will return "cancel"
        '''
        while True:
            var = input(prompt)
            if var == "quit" or var =="q" or var == "cancel" or var == "c":
                print("\nStopping current operation.")
                return "cancel"

            elif skippable and (var == "skip" or var =="s" or var =="stop" or var=="." or var==""):
                return "skip"

            elif type == "int":
                #Add support for list of integer input
                comma = var.find(",")
                if comma != -1:
                    var_list = var.split(",")
                    int_var_list = []
                    failure = False

                    i = 0
                    while i < len(var_list):
                        try:
                            int_var = int(var_list[i].strip())
                            int_var_list.append(int_var)
                            i+=1
                        except:
                            print("Not an integer")
                            failure = True
                            break

                    if failure:
                        print("list contains one or more non-integers")
                        continue

                    if range == False:
                        return int_var_list

                    else:
                        failure = False
                        for num in int_var_list:
                            if num not in range:
                                failure = True
                                break

                        if not failure:
                            return int_var_list
                        
                        print("list contains one or more out of bounds integers")                           

                else:
                    try: 
                        var = int(var)
                    except:
                        print("Not an integer")
                        continue
                    if range == False:
                        break
                    elif range != False and var in range:
                        break
                   
                print("Invalid input, please try again with valid integer...")

            elif type == "str":
                if len(var) > 0:
                    #added list support
                    lowerVar = var.lower()
                    comma = lowerVar.find(",")
                    if comma != -1:
                        lowerVar = lowerVar.split(",")
                        if range == False:
                            return lowerVar

                        failure = False
                        ret = []

                        for s in lowerVar:
                            tmp = s.strip() #remove whitespace on both sides

                            if len(tmp) not in range:
                                print("One of more strings is too long/short")
                                failure = True
                                break
                            else:
                                ret.append(tmp)

                        if not failure:
                            return ret

                    else: #just single string
                        if range != False and len(var) in range:
                            break
                        elif range == False:
                            break
                print("Invalid input, please try again with a non-null string or list of strings...")

            elif type == "bool":
                lowerVar = var.lower()
                if lowerVar == "false":
                    var = False
                elif lowerVar == "true":
                    var = True
                elif lowerVar == "y" or lowerVar == "yes":
                    var = True
                elif lowerVar == "n" or lowerVar == "no":
                    var = False
                else:
                    print("Invalid input, please try with 'true' or 'false'...")
                    continue

                break

            elif type == "time":
                lowerVar = var.lower()
                if (len(lowerVar) in [3,4,5,6,7,8]) and (lowerVar.find(":") != -1):
                    t = Time(lowerVar)
                    if t.hour == 0 and t.minute == 0: #error
                        print("Invalid input, time must be 24 hour hh:mm or h:mm or 12 hour with pm at end...")
                        continue
                    else:
                        return t

            else:
                print("Provided invalid type... must be 'str', 'int', or 'bool'")
                return None

        return var   

    def cmdNotRecognized(self, cmd):
        '''
            Standardizes command not recognized error message
        ''' 
        print("Command '%s' not recognized, type help for more info"%cmd)

if __name__=="__main__":
    
    if len(sys.argv) == 3 or len(sys.argv) == 4:
        year = None
        month = None
        try:
            year = int(sys.argv[2])
            month = int(sys.argv[1])
        except:
            print("usage: [month(numeric)] [year]")
            sys.exit(0)

        if year not in range(0,2500) or month not in range(1,13):
            print("Year/Month invalid")
            sys.exit(0)

        else:
            if "debug" in sys.argv:
                test = Scheduler_UI(month, year, True)

            else:
                test = Scheduler_UI(month, year)
                sys.exit(0)

    if "debug" in sys.argv:
        test = Scheduler_UI(None, None, True)
    else:
        test = Scheduler_UI()
        sys.exit(0)
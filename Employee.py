#Employee class
import pickle

from Time import Time
from Rule import Rule

class Employee:

	def __init__(self, name, priority):
		'''
			@param name: String name of the employee
			@param priority: integer, lower priority is better
		'''
		self.name = name
		self.priority = priority
		self.rules = []
		self.curShifts = 0 #how many shifts an employee has
		self.shiftsPerWeek=[0,0,0,0,0] #counts num shifts per week

	def save(self, file, info=False):
		'''
			Saves employee data
			@param file: a file pointer open in "wb" mode
			@params info: T/F whether to print additional info while saving.
		'''
		print("  Saving data for %s..."%(self.name))
		pickle.dump(self.name, file)
		pickle.dump(self.priority, file)
		pickle.dump(self.curShifts, file)
		pickle.dump(self.shiftsPerWeek, file)
		if info: print("    Saved employee attributes")
		pickle.dump(len(self.rules), file)
		if info: print("    %d rules to save"%len(self.rules))
		i = 0
		for r in self.rules:
			r.save(file, i, info)
			i+=1

		return True

	def load(self, file, info = False):
		'''
			Loads employee data
			@param file: a file pointer open in "rb" mode
			@params info: T/F whether to print additional info while loading.
			@return True if load was successful, False if any error occured
		'''
		try:
			self.name = pickle.load(file)
			print("  Loading data for %s..."%self.name)
			self.priority = pickle.load(file)
			if info: print("    Read priority: %d"%self.priority)
			self.curShifts = pickle.load(file)
			if info: print("    Read number of shifts: %d"%self.curShifts)
			self.shiftsPerWeek = pickle.load(file)
			if info: print("    Read shifts per week: %s"%self.shiftsPerWeek)
			numRules = pickle.load(file)
			if info: print("    Read number of rules: %d"%numRules)

			print("    %d rules to load"%numRules)
			self.rules = []
			num = 0
			for i in range(0,numRules):
				r = Rule()
				if not r.load(file, num, info):
					print("\nError (%s): Loaded invalid rule, aborting..."%self.name)
					return False
				self.setRule(r)
				num += 1

		except Exception as e:
			print("\nError: %s while loading %s"%(str(e), self.name))
			return False

		if info: print("  Finished loading data for %s"%self.name)
		return True

	def setRule(self, rule):
		'''
			Adds a Rule object rule to employee
			@params rule: a Rule object to be added to the employee
		'''
		if rule.__class__.__name__ == "Rule":
			self.rules.append(rule)

	def getRules(self):
		'''
			@return: list of Rule objects, all rules asigned to this employee
		'''
		return self.rules

	def getRule(self, index):
		'''
			@return: a single Rule object
		'''
		return self.rules[index]

	def deleteRule(self, mrule):
		'''
			Deletes rule from self.rules that matches mrule
			@param mrule: rule object to match
			@return: 1 if successful, -1 if no match
		'''
		for r in self.rules:
			if mrule == r:
				self.rules.remove(r)
				return 1
		return -1

	def matchRule(self, shiftRule):
		'''
			Given keyword arguments as in Rule class it determines if employee's stored rules match this rule
			A match is when one or more of the rules match given rule
			@params lunch = True if this is a lunch shift False if this is a dinner shift
			@params time = string "h:mm" hour at which shift starts
			@params weekday = 0-6 indicating which day of the week, 0=Monday, 6=Sunday
			@params weeknum = 1-4, applies rule to a specific week of the month
			@params daynum = 1-31, applies rule to a specific day of the month

			weekday, weeknum, daynum CANNOT be lists

			@return: -1 if rule is invalid, False if no match, True if match
		'''
		matchRule = shiftRule.getDict()

		if "maxshifts" in matchRule.keys():
			print("maxshifts rule not allowed")
			return -1

		if "maxshiftsPW" in matchRule.keys():
			print("maxshiftsPW rule not allowed")
			return -1		

		if "lunch" not in matchRule.keys():
			print("must specify lunch=True/False")
			return -1

		assert len(matchRule) == 5, "Shift Rule must be complete"

		lunch = matchRule["lunch"]
		allowed = False #match occurs if atleast 1 rule fits
		
		for r in self.rules:
			print("Allowed? %s"%allowed)
			print("curRule:\n%s"%r)
			emp_rule = r.rule

			if "maxshifts" in emp_rule:
				if ((self.curShifts+1)<=emp_rule["maxshifts"]) == False:
					print("Already at MaxShifts")
					return False
				else:
					continue

			if "maxshifspw" in emp_rule:
				cur_weeknum = matchRule["weekday"]
				if (self.shiftPerWeek[cur_weeknum-1]+1) >= emp_rule["maxshiftspw"]:
					print("Already max shifts for this week")
					return False
				else:
					continue

			if "exclude" in emp_rule:
				if self._matchLunchField(emp_rule, lunch):
					if matchRule["daynum"][0] in emp_rule["exclude"]:
						#daynum specified is excluded so return False
						return False


			if "daynum" in emp_rule: #means rule should have fields lunch (optional), time, daynum only dont take into account anything else
				# assert len(rule) == 3, "Rule has invalid format"

				if self._matchLunchField(emp_rule, lunch): # matches lunch fields in both rules
					print("Matched lunch field")

					if matchRule["daynum"][0] in emp_rule["daynum"]:
						print("daynum matched")
						
						if emp_rule["time"] <= matchRule["time"]: #employee can work at or before that time
							allowed = True
						else:
							print("time match failed")
							# print(type(emp_rule["time"]))
							# print(type(matchRule["time"]))
							# print("x <= y: %s"%(emp_rule["time"] <= matchRule["time"]))
							# print(emp_rule["time"])
							# print(matchRule["time"])
						
					else:
						print("daynum failed")
						# print(type(matchRule["daynum"]))
						continue

				else: #doesnt match lunch field
					print("lunch field match failed, skipping rule")
					continue

			elif "weekday" in emp_rule: #rule will match with fields lunch(optional), time, weekday, weeknum(optional)

				if self._matchLunchField(emp_rule, lunch):
					print("Matched lunch field")

					if matchRule["weekday"][0] in emp_rule["weekday"]:
						print("Weekday match")

						if ("weeknum" in emp_rule):
							if matchRule["weeknum"][0] in emp_rule["weeknum"]:
								print("employee rule has weeknum field and it matches")
								if emp_rule["time"] <= matchRule["time"]: #employee can work at or before that time
									allowed = True

							else:
								print("employee rule has weeknum field but it doesnt match")
								continue

						else:
							print("employee rule does not have weeknum field")
							if emp_rule["time"] <= matchRule["time"]: #employee can work at or before that time
								allowed = True

					else:
						print("Weekday mismatch")
						continue

				else:
					print("lunch field match failed, skipping rule")
					continue

			elif "weeknum" in emp_rule: #rule will match with lunch (optional) , time, weekday(optional)
				
				if self._matchLunchField(emp_rule, lunch):
					print("Matched lunch field")

					if matchRule["weeknum"][0] in emp_rule["weeknum"]:
						print("Weeknum match")

						if ("weekday" in emp_rule):
							if matchRule["weekday"][0] in emp_rule["weekday"]:
								print("employee rule has weekday field and it matches")
								if emp_rule["time"] <= matchRule["time"]: #employee can work at or before that time
									allowed = True

							else:
								print("employee rule has weekday field but it doesnt match")
								continue

						else:
							print("employee rule does not have weekday field")
							if emp_rule["time"] <= matchRule["time"]: #employee can work at or before that time
								allowed = True

					else:
						print("Weekday mismatch")
						continue

				else:
					print("lunch field match failed, skipping rule")
					continue 

			print("")

		print("Done matching employee %s, allowed = %s"%(self.name, allowed))
		return allowed

	def _matchLunchField(self, emp_rule, matchLunch):
		'''
			helper function to match optional lunch field if it is present in employee's rule
		'''
		if "lunch" in emp_rule:
			cur_lunch = emp_rule["lunch"]
			return cur_lunch == matchLunch
		else:
			return True #ommited lunch field means default yes for lunch and dinner

	def printRules(self):
		if len(self.rules) == 0:
			print("No Rules")
			print("")
		i = 1
		for r in self.rules:
			print("Rule %d:"%i)
			print(r)
			i+=1

	def getPriority(self):
		return self.priority

	def chgPriority(self, num):
		self.priority = num

	def getName(self):
		return self.name

	def curNumShifts(self):
		return self.curShifts

	def addShift(self, weeknum):
		'''
			Increases curShifts
		'''
		self.curShifts += 1
		self.shiftsPerWeek[weeknum-1] += 1

	def removeShift(self, weeknum):
		self.curShifts -= 1
		self.shiftsPerWeek[weeknum-1] -= 1

	def __lt__(self, other):
		if other.__class__.__name__ != "Employee":
			return False
		if self.priority < other.priority:
			return True
		return False

	def __eq__(self, other):
		if other.__class__.__name__ != "Employee":
			return False
		if self.name == other.name:
			return True
		return False

	def __le__(self,other):
		if other.__class__.__name__ != "Employee":
			return False
		return self.__lt__(other) or (self.priority == other.priority)

	def __ge__(self,other):
		if other.__class__.__name__ != "Employee":
			return False
		return  not self.__lt__(other)

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.name

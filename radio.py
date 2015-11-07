#!usr/bin/env python

import sys
import os
import Queue
import time

#*************************************** Report **************************************************
""" Assignment 4: Part2-Programming Question 
		Manish Kumar

As it was obvious that problem belonged to the category of Constraint Satisfaction Problem, So
I decided to solve it by applying backtracking. Now, to reduce the number of backtracks and time 
elapsed, I have used variable ordering i.e MRV (Minimum Remaining Values) and assigned LCV (Least 
Constraining Value) to the variable first. For choosing the value for a state, I am also checking 
whether this assignment causes any future conflicts with it's neighbor or not. By checking Arc 
consistency, I have ensured that all  the future constraint violation is detected as early as
possible and remove all the conflicting  frequency from the domains of all other states. I am also
checking whether with given legacy constraint solution is feasible or not before searching for the 
solution by calling arc consistency function. All these preprocessing helped into reducing the number 
of bactracks. Now this program makes no backtrack and gives the solution in first attempt for all 
the test cases provided.

Assumptions:  For adjacent states file, I have hard coded the filename. So, In order to run the program
with different file, change the name of the file in the load_data function. Similarly, for output file
I have hardcoded the name of output file as "results.txt".

Analysis: This program works really well. As for given all the test cases, it makes no backtrack and
takes time even less than 0.1 second. It can be further improved by taking the advantage of structure
and removing some of the variables to convert rest of the graph into a tree. This may result into even 
lesser time.
"""
#***************************************************************************************************

start = time.time()

neighbors = {}
frequency = {}

def load_data():
	global neighbors,frequency
	with open('adjacent-states', 'r') as file:
	       for line in file:
	            lst = line.split()
		    if len(lst) > 0:			#checking whether entry is valid or not
	            	neighbors[lst[0]] = lst[1:]
	filename = sys.argv[1]
	with open(filename , 'r') as file:
		try:
			for line in file:
				(city, freq) = line.split()
				frequency[city]=[freq]
		except ValueError:
			frequency = {}
	for key in neighbors:
		if key not in frequency and neighbors[key] != []:   # If a state has no neighbor, We can give any values to it and save the 
			frequency[key] = ['A','B','C','D']	    # time in backtracking
		elif key not in frequency:
			frequency[key] = ['A']

# function mrv provides the next state whose frequency should be assigned by the backtracking function. 
# It first checks which state has minimum number of available frequency and in case of tie which has most neighbouring states. 

def mrv(assignment,frequency):
	global neighbors
	len_domain={}
	for key in frequency:
		if key not in assignment:
			len_domain[key]=len(frequency[key])
	val = sorted(len_domain.items(), key=lambda x: x[1])
	min_val = val[0][1]
	highest = 0
	mrv_state = val[0][0]
	for k in val:
		if k[1] > min_val:
			break
		(state,curr) = k
		if len(neighbors[state]) > highest:
			highest = len(neighbors[state])
			mrv_state = state
	return mrv_state

# function lcv returns a list of possible values for a state by ordering values such that value causes least conflict
# comes first in the list

def lcv(var,assignment,frequency):
	choices = frequency[var]
	conflict_queue =Queue.PriorityQueue()
	lcv_lst=[]
	for choice in choices:
		value = count_conflicts(var,choice,frequency,assignment)
		conflict_queue.put((value,(choice,)))
	while conflict_queue.empty() is not True:
		(value,(choice,)) = conflict_queue.get()
		lcv_lst.append(choice)
	return lcv_lst

# Assign Frequency value to the State in the assignment dictionary
def assign(var,value,assignment):
	assignment[var]=value

# In case of bactracking, remove the values from the assignment dictionary
def delete_assign(var,assignment):
	if var in assignment:
		del assignment[var]

# Check if new assignment causes a conflict with existing assignment of neighboring states
def Isconflict(var,value,assignment):
	for state in neighbors[var]:
		if state in assignment and assignment[state] == value:
			return True
	return False	

# Temporary assign the value to a state. Remove the rest of the frequency from state's domain,append it to a list and return the list
def temp_assign(var,value,frequency):
	remove_freq = []
	for k in frequency[var]:
		if k != value:
			remove_freq.append((var,k))
	frequency[var]= [value]
	return remove_freq

# In case of backtrack, append the removed frequency from the state's domain
def reassign(remove_lst,frequency):
	for k in remove_lst:
		(var,val) = k
		frequency[var].append(val)

# Count the number of future conflicts caused by the possible assignment of the frequency to the state.
def count_conflicts(var,choice,frequency,assignment):
	global neighbors
	count = 0
	con_queue = Queue.Queue()
	for neighbor in neighbors[var]:
		if neighbor not in assignment:
			con_queue.put((neighbor,choice))
	while not con_queue.empty():
		(state,mychoice) = con_queue.get()
		if len(frequency[state]) == 1 and [choice] == frequency[state] :
			count += 10
		if mychoice in frequency[state]:
			count += 1
	return count
	
# Check whether frequency assignment caused any violation of constraint or not and return the result.
def arc_consistent(assignment,frequency,var=None,remove_lst=None):
	global neighbors
	myqueue = Queue.Queue()
	if var == None:
		for state in neighbors:
			for neighbor in neighbors[state]:
				myqueue.put((state,neighbor))
	else:
		for neighbor in neighbors[var]:
			myqueue.put((neighbor,var))
	while not myqueue.empty():
		(state,neighbor) = myqueue.get()
		if remove_inconsistent(state,neighbor,remove_lst):
			if frequency[state] == []:
				return False
			for new_neigh in neighbors[state]:
				myqueue.put((new_neigh,state))
	return True

# Remove all the frequency from the domain of a state that violates the constraint.
def remove_inconsistent(state,neighbor,remove_lst):
	removed = False
	for freq in frequency[state]:
		if len(frequency[neighbor]) == 1 and [freq] == frequency[neighbor] :
			if remove_lst != None:
				remove_lst.append((state,freq))
			frequency[state].remove(freq)
			removed = True
	return removed

# To count the number of bactracks in the program
def myfunc():
	myfunc.counter += 1
	
		

# Main backtracking function that assigns values to a state and checks whether this assignment violates the constraint or not.
# If an assignment violates the constraints, function removes the assignment and backtrack to try another assignment.	
def backtrack(assignment,frequency):
	myfunc.counter = 0
	if len(assignment) == len(frequency):
		return assignment
	var = mrv(assignment, frequency)
	for value in lcv(var, assignment,frequency):
		if False == Isconflict(var, value, assignment):
			assign(var, value, assignment)
			remove_lst = temp_assign(var, value,frequency)
			if arc_consistent(assignment, frequency,var, remove_lst):
				result = backtrack(assignment,frequency)
				if result != None:
					return result
			reassign(remove_lst,frequency)
	myfunc()							# Counting the no. of backtracks
	delete_assign(var, assignment)
	return None

# with given constraints, this function search for the solution and report if it does not exist.
def search_solution(frequency):
	assignment = {}
	for state in frequency:					# Here all those states, which has just one frequency in their domain, have 
		if len(frequency[state])== 1:			# been assigned to the assignment dictionary and then checking it's consistency
			value = (frequency[state])[0]		
			assign(state,value,assignment)
	
	if arc_consistent(assignment,frequency) == False:	# If legacy_constraints provides such values that no assignment is feasible
		print " No Solution is Feasible"		# satisfying the constraints, then no solution can be predicted at this stage

	
	if backtrack(assignment,frequency) == None :
		print " No assignment is valid"
	else:	
		with open("results.txt","w") as file:
			for key in assignment:
				file.write( str(key) + " :    " + str(assignment[key]))
				file.write("\n")
		file.close()

if __name__ == "__main__":
	load_data()
	search_solution(frequency)	
	end = time.time()
	print " Total Elapses time:  " + str(end - start)
	print "\n"
	print "Number of backtracks:  " + str(myfunc.counter)

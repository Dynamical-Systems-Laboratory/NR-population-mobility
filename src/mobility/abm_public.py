# ------------------------------------------------------------------
#
#	Module for generation of public places in an ABM population
#
# ------------------------------------------------------------------

import math

class Workplaces(object):
	''' Class for generation of workplaces '''

	def __init__(self, fname_NR, fname_outside, fmap):
		''' Generate individual workplaces from input data.
				Generates all workplaces, including outside New Rochelle. '''

		# fname_NR - all public places in New Rochelle
		# fname_outside - all public places outside NR 		
		# fmap - name of the file with types and descriptions
		#			Currently applicable only to New Rochelle.
		#

		# Total number of workplaces
		self.ntot = 0

		# Data
		# Buildings
		self.workplaces = []
		# Type map
		self.workplace_map = {}
		# Type representing daycares
		self.daycare_type = 'FF'

		# New Rochelle
		# Load the buildings and the map
		# (first the map)
		self.read_gis_types(fmap)
		self.read_gis_data(fname_NR)

		# Outside of New Rochelle
		self.read_outside_data(fname_outside)

	def read_gis_data(self, fname):
		''' Read and store workplace data for 
				all workplaces in New Rochelle '''

		with open(fname, 'r') as fin:
			# Skip the header
			next(fin)
			ID = 0
			for line in fin:
				temp = {}
				line = line.strip().split()

				# Exclude hospitals, retirement homes, 
				# and schools
				if (line[0] is 'H') or ('AA' in line[0]) or (line[0] is 'F'):
					continue

				ID += 1
				# Common information
				temp['ID'] = ID
				# Non zero only for schools, retirement homes, and hospitals
				temp['specialID'] = 0
				temp['type'] = line[0]
				temp['lon'] = float(line[2])
				temp['lat'] = float(line[1])
				# Current number of employees
				temp['N_emp'] = 0
				# Min and max number of employees for that type
				temp['N_min'] = self.workplace_map[temp['type']][1]
				temp['N_max'] = self.workplace_map[temp['type']][2]

				self.workplaces.append(temp)
		self.ntot = ID
		print('Loaded ' + str(ID) + ' NR workplaces')

	def read_gis_types(self, fname):
		''' Loads a map with GIS public building types and descriptions, 
				minimum and maximum capacity of that type '''

		with open(fname, 'r') as fin:
			for line in fin:
				line = line.strip().split()
				self.workplace_map[line[0]] = [(' ').join(line[1:-2]), int(line[-2]), int(line[-1])]
	

	def read_outside_data(self, fname):
		''' Read and store workplace data for 
				all workplaces outside of New Rochelle. 
				It groups the workplaces by zipcode,
				all the places with the same zipcode will 
				be treated as a single workplaces with 
				average coordinate of all of them. '''

		ID = self.ntot

		# Read and group by zipcodes 
		all_out = {}
		with open(fname, 'r') as fin:
			for line in fin:
				line = line.strip().split(',')
				
				zipcode = str(int(line[2]))
				if zipcode in all_out:
					all_out[zipcode][0].append(float(line[0]))
					all_out[zipcode][1].append(float(line[1]))
					all_out[zipcode][2] += 1
				else:
					all_out[zipcode] = [[float(line[0])],[float(line[1])], 1]
		
		# Add each zipcode as a workplace
		# Coordinates are averaged GIS
		for key, value in all_out.items():
			lat = sum(value[0])/value[2]
			lon = sum(value[1])/value[2]

			temp = {}
			ID += 1

			temp['ID'] = ID
			# Non zero only for schools, retirement homes, and hospitals
			temp['specialID'] = 0
			temp['type'] = 'outside' 
			temp['lat'] = lat 
			temp['lon'] = lon 
			temp['zip'] = int(key)

			self.workplaces.append(temp)

		print('Loaded ' + str(ID-self.ntot) + ' outside workplaces')
		self.ntot = ID		

	def merge_with_special_workplaces(self, schools, retirement_homes, hospitals):
		''' Add the workplace categories that are modeled separately otherwise '''
	
		ID = self.ntot
		for school in schools:
			ID += 1
			temp = {}
			temp['ID'] = ID
			temp['specialID'] = school['ID']
			temp['type'] = 'F'
			temp['lon'] = school['lon']
			temp['lat'] = school['lat']
			# Current number of employees
			temp['N_emp'] = 0
			# Min and max number of employees for that type
			if school['school type'] == 'daycare':  
				temp['N_min'] = self.workplace_map[self.daycare_type][1]
				temp['N_max'] = self.workplace_map[self.daycare_type][2]
			else:
				temp['N_min'] = self.workplace_map[temp['type']][1]
				temp['N_max'] = self.workplace_map[temp['type']][2]
		
			self.workplaces.append(temp)
		
		for rh in retirement_homes:
			ID += 1
			temp = {}
			temp['ID'] = ID 
			temp['specialID'] = rh['ID']
			temp['type'] = 'AA'
			temp['lon'] = rh['lon']
			temp['lat'] = rh['lat'] 

			# Current number of employees
			temp['N_emp'] = 0
			# Min and max number of employees for that type
			temp['N_min'] = self.workplace_map[temp['type']][1]
			temp['N_max'] = self.workplace_map[temp['type']][2]

			self.workplaces.append(temp)

		for hospital in hospitals:
			ID += 1
			temp = {}
			temp['ID'] = ID 
			temp['specialID'] = hospital['ID']
			temp['type'] = 'H'
			temp['lon'] = hospital['lon']
			temp['lat'] = hospital['lat']

			# Current number of employees
			temp['N_emp'] = 0
			# Min and max number of employees for that type
			temp['N_min'] = self.workplace_map[temp['type']][1]
			temp['N_max'] = self.workplace_map[temp['type']][2]

			self.workplaces.append(temp)

		self.ntot = ID

	def __repr__(self):
		''' String output for stdout or files '''
		
		temp = []
		for place in self.workplaces:
			temp.append((' ').join([str(place['ID']), str(place['lat']), str(place['lon']), str(place['type']), str(place['specialID'])])) 
	
		return ('\n').join(temp)
			
class Schools(object):
	''' Class for generation of schools '''

	def __init__(self, fname, fmap):
		''' Generate individual schools from input data '''

		#
		# fname - input file name with all public places
		# fmap - name of the file with types and descriptions
		#

		# Total number of schools 
		self.ntot = 0

		# Data
		# Buildings
		self.schools = []
		# Type map
		self.schools_map = {}

		# Type hierarhy
		self.school_types = {'daycare' : 1, 'primary' : 2, 'middle' : 3, 'high' : 4, 'college' : 5}
		self.school_strings = ['daycare', 'primary', 'middle', 'high', 'college']

		# Load the buildings and the map
		self.read_gis_data(fname)
		self.read_gis_types(fmap)

	def read_gis_data(self, fname):
		''' Read and store school data '''

		with open(fname, 'r') as fin:
			# Skip the header
			next(fin)
			ID = 0
			for line in fin:
				line = line.strip().split()

				# Include only schools
				if line[0] is not 'F':
					continue

				# If one school has multiple levels,
				# split into each level but keep min/type
				# info for reference

				# Add lowest and highest type
				school_type = line[5].split(',')
				min_type = 1000
				max_type = 0
	
				for sc in school_type:
					sc = sc.strip()
					temp_type = self.school_types[sc]
					if temp_type < min_type:
						min_type = temp_type
						min_str = sc
					if temp_type > max_type:
						max_type = temp_type
						max_str = sc
			
				i0 = self.school_strings.index(min_str)
				iF = self.school_strings.index(max_str)
				for ii in range(i0, iF+1):
					temp = {}
					temp['school min type'] = self.school_strings[i0]
					temp['school max type'] = self.school_strings[iF]

					ID += 1
					# Common information
					temp['ID'] = ID
					temp['type'] = line[0]
					temp['lon'] = float(line[2])
					temp['lat'] = float(line[1])
					temp['school type'] = self.school_strings[ii]

					# Number of students always second after
					# coordinates; round and ignore differences
					# is is approximate
					num_types = iF-i0+1
					temp['num students'] = math.floor(float(line[4])/num_types)
					self.schools.append(temp)
				self.ntot = ID

	def read_gis_types(self, fname):
		''' Loads a map with GIS public building types and descriptions '''
	
		with open(fname, 'r') as fin:
			for line in fin:
				line = line.strip().split()
				self.schools_map[line[0]] = (' ').join(line[2:])
	
	def __repr__(self):
		''' String output for stdout or files '''
		
		temp = []
		for place in self.schools:
			temp.append((' ').join([str(place['ID']), str(place['lat']), str(place['lon']), place['school type']])) 
	
		return ('\n').join(temp)

class Hospitals(object):
	''' Class for generation of hospitals '''

	def __init__(self, fname, fmap):
		''' Generate individual hospitals from input data '''

		#
		# fname - input file name with all public places
		# fmap - name of the file with types and descriptions
		#

		# Total number of hospitals
		self.ntot = 0

		# Data
		# Buildings
		self.hospitals = []
		# Type map
		self.hospitals_map = {}

		# Load the buildings and the map
		self.read_gis_data(fname)
		self.read_gis_types(fmap)

	def read_gis_data(self, fname):
		''' Read and store hospital data '''

		with open(fname, 'r') as fin:
			# Skip the header
			next(fin)
			ID = 0
			for line in fin:
				temp = {}
				line = line.strip().split()

				# Include only hospitals 
				if line[0] is not 'H':
					continue
				
				ID += 1
				# Common information
				temp['ID'] = ID
				temp['type'] = line[0]
				temp['lon'] = float(line[2])
				temp['lat'] = float(line[1])

				# Number of patients
				temp['num patients'] = int(line[4])

				self.hospitals.append(temp)

		self.ntot = ID

	def read_gis_types(self, fname):
		''' Loads a map with GIS public building types and descriptions '''
	
		with open(fname, 'r') as fin:
			for line in fin:
				line = line.strip().split()
				self.hospitals_map[line[0]] = (' ').join(line[2:])
	
	def __repr__(self):
		''' String output for stdout or files '''
		
		temp = []
		for place in self.hospitals:
			temp.append((' ').join([str(place['ID']), str(place['lat']), str(place['lon'])])) 
	
		return ('\n').join(temp)

class RetirementHomes(object):
	''' Class for generation of retirement and nursing homes '''

	def __init__(self, fname, fmap):
		''' Generate individual retirement and nursing homes from input data '''

		#
		# fname - input file name with all public places
		# fmap - name of the file with types and descriptions
		#

		# Total number of retirement and nursing homes
		self.ntot = 0

		# Data
		# Buildings
		self.retirement_homes = []
		# Type map
		self.retirement_homes_map = {}

		# Load the buildings and the map
		self.read_gis_data(fname)
		self.read_gis_types(fmap)
	
	def read_gis_data(self, fname):
		''' Read and store retirement homes data '''

		with open(fname, 'r') as fin:
			# Skip the header
			next(fin)
			ID = 0
			for line in fin:
				temp = {}
				line = line.strip().split()

				# Include only retirement homes
				if not (line[0] in 'AA'):
					continue
				
				ID += 1
				# Common information
				temp['ID'] = ID
				temp['type'] = line[0]
				temp['lon'] = float(line[2])
				temp['lat'] = float(line[1])

				# Number of residents
				temp['num residents'] = int(line[4])

				self.retirement_homes.append(temp)

		self.ntot = ID-1

	def read_gis_types(self, fname):
		''' Loads a map with GIS public building types and descriptions '''
	
		with open(fname, 'r') as fin:
			for line in fin:
				line = line.strip().split()
				self.retirement_homes_map[line[0]] = (' ').join(line[2:])
	
	def __repr__(self):
		''' String output for stdout or files '''
		
		temp = []
		for place in self.retirement_homes:
			temp.append((' ').join([str(place['ID']), str(place['lat']), str(place['lon'])])) 
	
		return ('\n').join(temp)

class LeisureLocations(object):
	''' Class for generation of leisure locations '''

	def __init__(self, fname):
		''' Load and pre-process leisure locations - in a broad sense,
				grocerry stores are also included. '''

		#
		# fname - input file name with all public places
		#			that are also counted as leisure locations
		#

		# Total number of leisure locations
		self.ntot = 0

		# Data
		# Buildings
		self.leisure_locations = []

		# Load the buildings 
		self.read_gis_data(fname)
	

	def read_gis_data(self, fname):
		''' Read and store data for 
				all leisure locations in New Rochelle '''

		with open(fname, 'r') as fin:
			# Skip the header
			next(fin)
			ID = 0
			for line in fin:
				temp = {}
				line = line.strip().split(',')
				ID += 1
				# Common information
				temp['ID'] = ID
				temp['name'] = line[0]
				# Type may have commas
				leisure_type = line[1]
				# If not found, crash it
				lat_pos = len(line)
				for il in range(2,len(line)):
					try: 
						float(line[il])
						lat_pos = il
						break
					except ValueError:
						leisure_type += (',' + line[il])

				temp['type'] = leisure_type
				temp['lat'] = float(line[lat_pos])
				temp['lon'] = float(line[lat_pos+1])

				self.leisure_locations.append(temp)
		self.ntot = ID
		print('Loaded ' + str(ID) + ' NR leisure locations')

	def __repr__(self):
		''' String output for stdout or files '''
		
		temp = []
		for place in self.leisure_locations:
			temp.append((' ').join([str(place['ID']), str(place['lat']), str(place['lon'])])) 
	
		return ('\n').join(temp)






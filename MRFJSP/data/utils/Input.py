import numpy as np

class Input:
	def __init__(self, inputFile: str):
		self.machines = [] 
		self.operations = []
		self.__proNum = []
		self.__lines = None
		self.__input = inputFile
		self.Mac_Num = 0
		self.Job_Num = 0
		self.quant_operations_per_jobs = []

	def __readExample(self):
		with open(self.__input) as fileObject:
			self.__lines = fileObject.readlines()
		
		self.__lines[0] = self.__lines[0].strip().split("\t")

		self.Job_Num =  int(self.__lines[0][0])
		self.Mac_Num = int(self.__lines[0][1])

		del self.__lines[0]

		for i in range(len(self.__lines)):
			self.__lines[i] = self.__lines[i].strip().split(" ")
			operation = int(self.__lines[i].pop(0)) # mỗi dòng là 1 job, phần tử đầu tiên là số operation của mỗi job
			self.quant_operations_per_jobs.append(operation)
			self.__proNum.append(operation)
			while "" in self.__lines[i]:
				self.__lines[i].remove("")
	
	def __initMatrix(self):
		for i in range(len(self.__proNum)): # = số lượng job
			self.machines.append([])
			self.operations.append([])
			for _ in range(self.__proNum[i]): # = số operation của mỗi job
				self.machines[i].append([])
				self.operations[i].append([])
				
	def getMatrix(self):
		self.__readExample()
		self.__initMatrix()
		for i in range(len(self.__lines)): # lặp qua các dòng (các job)
			lo  = 0 
			hi = 0 
			for j in range(self.__proNum[i]): # lặp qua các operation của job
				head = int(self.__lines[i][lo]) # số cặp <machine, process_time>
				hi = lo + 2*head + 1

				lo += 1
				while lo < hi: # lặp qua các cặp <machine, process_time>
					self.machines[i][j].append(int(self.__lines[i][lo]))
					self.operations[i][j].append(int(self.__lines[i][lo + 1]))
					lo += 2
		
		p_table = self.DataConversion()
		return (p_table, self.quant_operations_per_jobs)

	def DataConversion(self):
		total_of_operations = np.sum(self.quant_operations_per_jobs)

		process_times = np.ones((total_of_operations, self.Mac_Num), dtype=int)*(-1)
		index = 0
		for (i1, i2) in zip(self.machines, self.operations): 
			for (j1, j2) in zip(i1, i2):
				for(k1, k2) in zip(j1, j2):
					process_times[index][k1-1]=k2
				index += 1
			
		return process_times

if __name__ == '__main__':
    inputFile = 'data/mk1.fjs'
    input = Input(inputFile)
    p_table, quant_operation_per_jobs = input.getMatrix()

    print(p_table)
	
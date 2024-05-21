import numpy as np

class Input:
    def __init__(self, inputFile: str):
        self.input = inputFile
        self.job_num = None
        self.machine_num = None
        self.num_op_per_jobs = []
        self.__lines = None

    def __readExample(self):
        with open(self.input) as fileObject:
            self.__lines = fileObject.readlines()
        
        self.__lines[0] = self.__lines[0].strip().split("\t")

        self.job_num = int(self.__lines[0][0])
        self.machine_num = int(self.__lines[0][1])
        del self.__lines[0]

        for i in range(len(self.__lines)):
            self.__lines[i] = self.__lines[i].strip().split(" ")
            operation_num = int(self.__lines[i].pop(0))
            self.num_op_per_jobs.append(operation_num)
            while "" in self.__lines[i]:
                self.__lines[i].remove("")
                    
    def getMatrix(self):
        self.__readExample()

        jobs = []        

        for i in range(len(self.__lines)):
            lo  = 0 
            hi = 0 
            job = []
            for j in range(self.num_op_per_jobs[i]): # lặp qua các operation của job
                head = int(self.__lines[i][lo]) # số cặp <machine, process_time>
                hi = lo + 2*head + 1
                lo += 1
                operation = []
                while lo < hi: # lặp qua các cặp <machine, process_time>
                    machine = int(self.__lines[i][lo])
                    pro_time = int(self.__lines[i][lo + 1])
                    operation.append((pro_time, machine))
                    lo += 2
                job.append(operation)
            jobs.append(job)
        
        return jobs
    
if __name__ == '__main__':
    inputFile = 'mk1.fjs'
    input = Input(inputFile)
    jobs = input.getMatrix()
    
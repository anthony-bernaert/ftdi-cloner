from .FTDIOperations import FTDIOperations, FTDIOperationType

class BatchCLI:
    def __init__(self, op : FTDIOperations):
        self.op = op

    def run(self, parameters : list[str]):
        print('Batch mode is not implemented yet. Please run in interactive mode by running the program without arguments.')
        print('Exiting...')
        pass
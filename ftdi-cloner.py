from modules.FTDIOperations import FTDIOperations
from modules.InteractiveCLI import InteractiveCLI
from modules.BatchCLI import BatchCLI
from sys import argv

op = FTDIOperations()
if len(argv) <= 1 or ('-i' in argv) or ('--interactive' in argv):
    cli = InteractiveCLI(op)
    cli.run()
else:
    cli = BatchCLI(op)
    cli.run(argv)

print("\nDone.")
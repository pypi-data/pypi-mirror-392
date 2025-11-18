
from .cli import main
import sys

def show_help():
	print("pymcdc — Modified Condition/Decision Coverage (MC/DC) Analyzer")
	print("--------------------------------------------------------------")
	print("Analyze and verify MC/DC criteria for Python programs.")
	print()
	print("Usage:")
	print("  python -m pymcdc [options] <source_file>")
	print()
	print("Main options:")
	print("  --run            Execute the program and show which MC/DC combinations were covered")
	print("  --append         Accumulate coverage data across multiple runs")
	print("  --unittest FILE  Run the source file using tests defined in FILE (can be used multiple times)")
	print("  --cover [+|-]L C R  Manually set requirement R of decision (L, C) as covered (+) or not (-)")
	print()
	print("Examples:")
	print("  python -m pymcdc foo.py")
	print("     → Analyze foo.py and display required condition combinations for each decision")
	print()
	print("  python -m pymcdc --run foo.py")
	print("     → Execute foo.py and display which MC/DC combinations were covered during execution")
	print()
	print("  python -m pymcdc --run --append foo.py")
	print("     → Cumulatively execute foo.py, aggregating MC/DC results from multiple runs")
	print()
	print("  python -m pymcdc --unittest test_foo.py foo.py")
	print("     → Run foo.py using unit tests from test_foo.py and show MC/DC coverage results")
	print()
	print("  python -m pymcdc --cover +5 5 1 -18 5 3 foo.py")
	print("     → Mark requirement 1 of decision (5,5) as covered and requirement 3 of (18,5) as not covered")
	print()
	print("Notes:")
	print("  • The number of MC/DC requirements for a decision with n conditions is not always n+1.")
	print("    It may be slightly larger due to algorithmic limitations.")
	print("  • For decisions with more than 15 conditions, analysis may take several minutes.")
	print("    When using --append, the computation for each decision is performed only once.")
	print()
	print("Installation:")
	print("  pip install pymcdc")
	print()
	print("Example:")
	print("  python3 -m pymcdc bissexto.py")
	print()
	print("Author: Marcio Delamaro")
	print("License: MIT")
	print()
	print("For more information, visit the project page.")


if __name__ == '__main__':
	if len(sys.argv) == 1:
		print('You should use one of the pymcdc commands or --help.')
	else:	
		match sys.argv[1]: 
			case '--help':
				show_help()
			case _:
				main()
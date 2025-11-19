from pyproteum import testnew, tcase, mutagen, exemuta, mutaview
import sys

def show_help():
	print("pyproteum — Mutation Testing Toolkit for Python")
	print("--------------------------------------------------")
	print("Implements mutation testing integrated with unittest.")
	print()
	print("Usage:")
	print("  python -m pyproteum <command> [options] <session_name>")
	print()
	print("Main commands:")
	print("  testnew   - Create a new test session")
	print("  tcase     - Manage test case files in a session")
	print("  mutagen   - Generate mutants")
	print("  exemuta   - Execute mutants and export results")
	print("  mutaview  - Inspect or build mutants")
	print()
	print("Example workflow:")
	print("  1. testnew → create a session")
	print("  2. tcase   → add or list test files")
	print("  3. mutagen → generate mutants")
	print("  4. exemuta → execute mutants")
	print("  5. mutaview→ view or export mutants")
	print()
	print("Examples:")
	print("  python -m pyproteum testnew --D /path --S foo.py mysession")
	print("  python -m pyproteum tcase --add --S test_foo.py mysession")
	print("  python -m pyproteum mutagen --create --ssdl 50 0 mysession")
	print("  python -m pyproteum exemuta --exec mysession")
	print("  python -m pyproteum mutaview --list mysession")
	print()
	print("Mutation operators available:")
	print("  cccr - Constant by Constant Replacement")
	print("  ccsr - Constant by Scalar Replacement")
	print("  crcr - Required Constant Replacement")
	print("  oaaa - Replace arithmetic assignment operator by other arithmetic assignment operator")
	print("  oaan - Replace arithmetic operator by other arithmetic operator")
	print("  oeap - Replace augmented assignment by plain assignment")
	print("  oepa - Replace plain assignment by augmented assignment")
	print("  oodl - Operator deletion")
	print("  orrn - Replace relational operator (<, >, <=, >=, ==, !=) by other relational operator")
	print("  sbrc - Replace each break statement by a continue statement")
	print("  scrb - Replace each continue statement by a break statement")
	print("  ssdl - Replace each statement by a pass statement")
	print()
	print("Options (general):")
	print("  --D <dir>      Set base directory for the session")
	print("  --S <file>     Specify source or test file(s)")
	print("  --x <list>     Specify mutant numbers")
	print("  --O <file>     Output file (CSV or mutant .py)")
	print("  --exec         Execute mutants")
	print("  --equiv        Mark mutants as equivalent")
	print("  --csv          Export results as CSV")
	print("  --view, --build, --gui  View mutants in terminal, generate file, or open GUI")
	print()
	print("Environment variable:")
	print("  PYPROTEUMCOLOR  Enable colored output")
	print()
	print("For more information, see the README or documentation site.")


if __name__ == '__main__':
	del sys.argv[0]
	if sys.argv ==[]:
		print('You should use one of the pyproteum commands or --help.')
	else:	
		match sys.argv[0]: 
			case 'testnew':
				testnew.main()
			case 'tcase':
				tcase.main()
			case 'mutagen':
				mutagen.main()
			case 'exemuta':
				exemuta.main()
			case 'mutaview':
				mutaview.main()
			case '--help':
				show_help()
			case _:
				print(f'Not found statement {sys.argv[0]}')


import getopt
import sys

from j21tool.upgrade import upgrade_to_java21
from j21tool.downgrade import downgrade_to_java11

def usage():
    print("""
j21-tool v0.0.1
usage: python -m j21tool (options) <base_dir>
options:
    -h, --help  show this help.
    -u, --java21 upgrade to java 21
    -1, --java11 downgrade to java 11
    -o, --output=<out_dir>, optional output directory, by default the original java files will be overwritten.
          
    <base_dir>  the base directory of a Java project.
""")

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu1o:", ["help", "java21", "java11", "output="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    project_dir = args[0] if len(args) > 0 else None 
    out_dir = 'f:/tmp/format'   

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-u", "--java21"):
            action = 'java21'
        elif o in ("-8", "--java8"):
            action = 'java8'
        elif o in ("-o", "--output"):
            out_dir = a
        else:
            assert False, "unhandled option"
    if not project_dir:
        usage()
        sys.exit(2)
    if action == 'java21':
        upgrade_to_java21(project_dir, out_dir)
    elif action == 'java11':
        downgrade_to_java11(project_dir, out_dir)
    else:
        usage()
        sys.exit(2)

if __name__ == "__main__":
    main()
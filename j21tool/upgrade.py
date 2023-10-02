import os
from pathlib import Path

#from javalang.tree import *
from j21tool.javalangex import *
from j21tool.javagen import generate_java
from j21tool.record import to_record
from j21tool.text_block import to_text_block

def upgrade_to_java21(project_dir, output_dir):

    path_project = Path(project_dir)
    project_parts_count = len(path_project.parts)
    pathlist = path_project.glob('**/*.java')
    for path in pathlist:
        rel_path_parts = path.parts[project_parts_count:]
        # excludes sub folders which start with '.'.
        if any(item.startswith('.') for item in rel_path_parts):
            continue

        upgrade_java(str(path), os.path.join(output_dir, *rel_path_parts))

def upgrade_java(java_file, output_file):
    print(f"converting {java_file}")
    with open(java_file) as f:
        codes = f.read()

    ast = parse(codes)
    rewrite_to_java21(ast)
    generate_java(ast, codes, output_file)

def rewrite_to_java21(ast):
    
    to_record(ast)
    to_text_block(ast)
    # to_pattern_match(ast)    

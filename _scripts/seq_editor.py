import sys; lines = open(sys.argv[1]).readlines(); lines[0] = lines[0].replace('pick', 'edit'); open(sys.argv[1], 'w').writelines(lines)

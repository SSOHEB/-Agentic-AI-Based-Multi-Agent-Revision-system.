import alembic.config
import os
import sys

def main():
    os.chdir(os.path.join(os.path.dirname(__file__), "backend"))
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    alembicArgs = [
        '--raiseerr',
        'revision', 
        '--autogenerate', 
        '-m', 
        'Add performance_log table'
    ]
    try:
        alembic.config.main(argv=alembicArgs)
        print("Revision created successfully.")
    except Exception as e:
        print("Error creating revision:", e)

    alembicArgs2 = [
        '--raiseerr',
        'upgrade', 
        'head'
    ]
    try:
        alembic.config.main(argv=alembicArgs2)
        print("Upgrade completed successfully.")
    except Exception as e:
        print("Error upgrading:", e)

if __name__ == '__main__':
    main()

import sys
import argparse
from App import create_app
from conf import env_factory

def run(args):
    env = env_factory(args.env)
    print(args.env)
    print(env.PORT)
    app=create_app(env)
    app.run(host=env.HOST, port=env.PORT)
def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    run_parsers = subparsers.add_parser("run")
    #run_parsers.add_argument('env',type=str,choices=["local","debug","testing","production"],default="local")
    run_group = run_parsers.add_mutually_exclusive_group(required=False)
    run_group.add_argument('-e','--env',choices=["local","debug","testing","production"],default="local")
    run_parsers.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

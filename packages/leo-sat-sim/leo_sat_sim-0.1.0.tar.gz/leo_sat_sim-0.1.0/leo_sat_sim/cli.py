# import argparse
# import os
# from .server import app   # import your Flask instance

# def main():
#     parser = argparse.ArgumentParser(
#         prog="leo-sat-sim",
#         description="Run the Satellite Visualization production server."
#     )

#     parser.add_argument(
#         "command",
#         choices=["runserver"],
#         help="Command to execute."
#     )

#     parser.add_argument(
#         "--host",
#         default="127.0.0.1",
#         help="Host to bind the server (default: 127.0.0.1)"
#     )

#     parser.add_argument(
#         "--port",
#         default=8080,
#         type=int,
#         help="Port to run the server on (default: 8080)"
#     )

#     args = parser.parse_args()

#     if args.command == "runserver":
#         print(f"🔧 Starting server at http://{args.host}:{args.port}")
#         app.run(host=args.host, port=args.port)


import click
from .server import app

@click.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8080)
def main(host, port):
    app.run(host=host, port=port)

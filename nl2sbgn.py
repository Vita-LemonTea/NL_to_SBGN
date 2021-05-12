import argparse

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--text",
                help="biochemical process description text")
ap.add_argument("-p", "--path",
                help="path to the description text")
args = vars(ap.parse_args())

if not args.get("path", False):
    text = args["text"]

else:
    with open(args["path"], "r") as f:
        text = f.read()
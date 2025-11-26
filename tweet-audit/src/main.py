import argparse
from application import Application
def main():
    parser = argparse.ArgumentParser(
        description="a command line service to handle extraction and analysis of X tweets from archives",
        formatter_class=argparse.RawTextHelpFormatter #Keeps all whitespace exactly as written
    )

    parser.add_argument(
            "command", #variable that stores the command passed
            nargs="?", #number of arguments to consume (? is for 0 or 1 value)
            choices=["extract-tweets", "analyze-tweets"],
            help="Command to execute",
        )
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return
    
    app = Application()
    if args.command == "extract-tweets":
        data = app.extract_tweets() 
        if not data.success:
            print(f"Error occured: {data.error_message}")
        print(f"successfully extracted: {data.count}")    
        
    if args.command == "analyze-tweets":
        app.analyze_tweets()
        if not data.success:
            print(f"an error occured: {data.error_message}")
        print(f"successfully analyized: {data.count} tweets") 
        
if __name__ == "__main__":
    main()
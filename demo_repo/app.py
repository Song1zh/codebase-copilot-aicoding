from uploader import upload_file
from parser import parse_config


def main():
    config = parse_config("config.json")
    result = upload_file("")
    print(result)


if __name__ == "__main__":
    main()
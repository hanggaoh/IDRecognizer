from formatFile import formatName

if __name__ == "__main__":
    with open("cat", "r") as f:
        for line in f:
            filename = line.rstrip().split("/")[-1]
            print(f"Original file: {filename}")

            print(f"Formated: {formatName("~/Movies/.a", filename)}")
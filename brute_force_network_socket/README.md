# Brute Force Network Socket

A script that can be used to brute force an application login over a network socket. 
Assumes that the application will prompt for a username and then a password after sending a banner.

```
usage: brute_force_network_socket.py [-h] [-l LIST] [-t TYPE] [-d DELIMITER] [-th THREADS] [-u USERNAME] [-v]
                host port

positional arguments:
  host                  Target IP address or hostname
  port                  Target port

optional arguments:
  -h, --help            show this help message and exit
  -l LIST, --list LIST  Path to username and/or password list
  -t TYPE, --type TYPE  Specify if you are using a list of passwords (p) or usernames and
                        password (up)
  -d DELIMITER, --delimiter DELIMITER
                        Delimiter in username and password list.
  -th THREADS, --threads THREADS
                        Number of threads to use.  Default is 5.
  -u USERNAME, --username USERNAME
                        Username to be used in conjunction with a password list.
  -v                    Adds verbosity. Not recommended when using multiple threads.

```
Results are written to a `brute_force_output.csv` file.

### Example using a username/password list
```
python3 brute_force_network_socket.py 10.11.1.72 4555 -l username_password_list.txt  -t up 
```

### Example using a password list
```
python3 brute_force_network_socket.py 10.11.1.72 4555 -l password_list.txt -t p -u admin
```

**Do not use for malicious purposes.  This script is for educational use only.**

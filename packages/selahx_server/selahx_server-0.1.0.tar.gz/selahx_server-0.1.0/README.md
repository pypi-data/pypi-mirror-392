# selahx_server
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
- Remote Access Tool — Fast and lightweight CLI experience.

- Designed for use with the selahx_client package (https://pypi.org/project/selahx_client), this enables remote access and management of files and have some control over a local machine from another device.

- Run https://pypi.org/project/selahx_server on the target machine, and https://pypi.org/project/selahx_client on the machine you want to control it from. 

- Follow each package’s guidelines for how to run it.

- For educational purposes only.
---

## Features

- overview: https://pypi.org/project/selahx_client

- github: https://github.com/Haabiy/selahx_client
---

## Usage

### Help

```bash
slx --help
````

![features](https://raw.githubusercontent.com/Haabiy/selahx_server/main/selahx/assets/slx_help.png)

---

### Server

1. Start the server on a specific host and port:

```bash
slx --key-file key.pem --port 1221 --ssh-host ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com
````

**Options:**

* `--key-file` — Path to the SSH private key
* `--port` — Local port for the server
* `--ssh-host` — SSH host (e.g., `ubuntu@ec2-xx-xxx-xx-xxx.compute-1.amazonaws.com`)

2. Run the client side via: https://pypi.org/project/selahx_client


### NB: 
- Ensure the port you configured on the target machine is open in your EC2 instance’s `inbound` and `outbound` rules, along with `SSH` for remote access.

- Grant Terminal access to the file system and other necessary resources (e.g: camera).

- Ensure your `.pem` file is executable. Check with `ls -l` (e.g., `-rwx------@ 1 Abiy staff 1678 Nov 15 22:36 key.pem`).

- If reverse tunneling fails to forward the connection, kill any active process using the same port. (use `kill $PID`)


## Requirements

* Python 3.11+
* Dependencies are managed via Poetry (see `pyproject.toml`)

---
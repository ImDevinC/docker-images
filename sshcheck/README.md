# sshcheck
This script is designed to query Github for a list of public SSH tokens assigned to an account and copy them into the authorized_hosts file on a machine. I use this to easily keep my servers up to date with any keys I've added to Github for remote SSH access. The script will overwrite the entire contents of the `authorized_hosts` file everytime it's ran, assuming any keys are returned. If no keys are returned, the file is not updated as it assumes an error occured.

## Usage
`docker run --rm -v ~/.ssh/authorized_hosts:/usr/src/app/authorized_hosts -e GITHUB_USER=imdevinc imdevinc/sshcheck`

There are two minimum requirements needed for the script to work properly.
The *GITHUB_USER* environment variable is the username of the Github user to get the tokens from.
*NOTE* No authentication is required to get the list of public SSH keys, so make sure you use your Github username so you don't inadvertently give someone else access to your SSH keys

By default, the script saves the list of keys to a file named `authorized_hosts` in the running directory. If you're running a docker image, be sure to mount your host images `~/.ssh/authorized_hosts` file to this location. If you want to change the location of the output file, you can set the `AUTHORIZED_HOSTS` environment variable.

Github does have a rate limit of 60 requests every hour, so make sure you don't run more than that as well.
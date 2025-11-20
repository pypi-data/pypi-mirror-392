#!/usr/bin/env python3
import argparse
import time
import os
import sys
import fnmatch
import multiCMD

version='0.22'
__version__ = version

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

USE_SUDO = True
if os.geteuid() == 0:
    USE_SUDO = False

if USE_SUDO:
    #check if sudo is available
    if multiCMD.run_command(['which','sudo'],quiet=True,return_code_only=True):
        print(f"{RED}sudo is required to run this script.{RESET}")
        sys.exit(1)

def execute_command(command,wait=True):
    if USE_SUDO:
        command = ['sudo'] + command
    return multiCMD.run_command(command,quiet=True,wait_for_return=wait)

def execute_commands(commands,wait=True):
    if USE_SUDO:
        commands = [['sudo']+command for command in commands]
    return multiCMD.run_commands(commands,quiet=True,wait_for_return=wait,max_threads=0)

def find_btrfs_mounts(filters):
    mounts = execute_command(["mount", "-t", "btrfs"])
    #mounts = multiCMD.run_command(["mount", "-t", "btrfs"],quiet=True)
    btrfs_mounts = set()
    if mounts:
        if filters:
            filters = [f'*{filter}*' for filter in filters]
            mount_list = [line.split()[2] for line in mounts]
            for filter in filters:
                btrfs_mounts.update(fnmatch.filter(mount_list,filter))
        else:
            btrfs_mounts.update([line.split()[2] for line in mounts])
    return btrfs_mounts

def parse_show_info(info):
    fs_used = None
    device_path = None
    uuid = None
    for line in info:
        if "uuid:" in line:
            uuid = line.split("uuid:")[1].split()[0].strip()
        if "Total devices" in line:
            fs_used = line.split("FS bytes used")[1].strip()
        if "path" in line:
            device_path = line.split("path")[1].strip()
    if fs_used is None or device_path is None or uuid is None:
        print(f"{RED}Could not parse btrfs show info.{RESET}")
        print(f"Output from btrfs filesystem show was:\n{info}")
    return uuid, fs_used, device_path

def parse_device_stats(stats):
    err_dict = {}
    for line in stats:
        key, val = line.split()
        err_dict[key.split(".")[-1]] = val
    return err_dict

def color_error_count(error_count):
    if int(error_count) == 0:
        return f"{GREEN}{error_count}{RESET}"
    elif int(error_count) < 10:
        return f"{YELLOW}{error_count}{RESET}"
    else:
        return f"{RED}{error_count}{RESET}"

def parse_scrub_status(output):
    scrub_data = {}
    lines = output
    # if "no stats available" in output:
    #     scrub_data = {
    #         "scrub_status": "Never",
    #         "scrub_time": "N/A",
    #         "scrub_rate": "N/A",
    #         "scrubbed_data": "N/A",
    #         "error_summary": "N/A"
    #     }
    # else:
    scrub_data = {
        "scrub_status": "Never",
        "scrub_time": "N/A",
        "scrub_rate": "N/A",
        "scrubbed_data": "N/A",
        "error_summary": "N/A"
    }
    for line in lines:
        if "Status:" in line:
            scrub_data["scrub_status"] = line.split(":")[1].strip()
        elif "Scrub started:" in line:
            scrub_data["scrub_time"] = line.split(":")[1].strip()
        elif "Rate:" in line:
            scrub_data["scrub_rate"] = line.split(":")[1].strip()
        elif "Total to scrub:" in line and scrub_data.get("scrub_status") != "running":
            scrub_data["scrubbed_data"] = line.split(":")[1].strip()
        elif "Bytes scrubbed:" in line and scrub_data.get("scrub_status") == "running":
            scrub_data["scrubbed_data"] = line.split(":")[1].strip()
        elif "Error summary:" in line:
            err_idx = lines.index(line)
            error_text = "\n".join(lines[err_idx:])
            if "no errors found" in error_text.lower():
                scrub_data["error_summary"] = f"{GREEN}OK{RESET}"  # Green-colored OK
            else:
                scrub_data["error_summary"] = F"{RED}{error_text}{RESET}"

    return scrub_data

def issue_scrub_command(mounts):
    # print(f"{YELLOW}Issuing scrub on {mount}{RESET}")
    # execute_command(['bash','-c',f"btrfs scrub start {mount}"],wait=False)
    # limit the number of mounts to scrub to max_scrub_count
    scrubed_mounts = []
    for mount in mounts:
        print(f"{YELLOW}Issuing scrub on {mount}{RESET}")
        execute_command(['btrfs','scrub','start',mount],wait=False)
        #multiCMD.run_command(['btrfs','scrub','start',mount],quiet=True)
        scrubed_mounts.append(mount)
        yield scrubed_mounts
    return scrubed_mounts


def main():
    parser = argparse.ArgumentParser(description="Check Btrfs filesystem status.")
    parser.add_argument("-s", "--scrub", help="Issue scrub to all pools", action="store_true")
    parser.add_argument("-i", "--interval", help="Interval for status check in seconds", default=2, type=int)
    parser.add_argument("-m", "--max_scrub_count", help="Maximum number of scrubs to issue at the same time", default=32, type=int)
    parser.add_argument("--scrub_command_lockout", help="Lockout for scrub command. Used to block two commands sent quickly.", default=10, type=int)
    parser.add_argument('pattern',nargs='*',help='Patterns to filter btrfs moutns. Default="*"')
    parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {version} stat btrfs by pan@zopyr.us")
    args = parser.parse_args()

    btrfs_mounts = set(find_btrfs_mounts(args.pattern))

    # If the scrub flag is enabled, issue the scrub command to all mounts
    if args.scrub:
        if args.max_scrub_count < 1:
            scrub_count = os.cpu_count()
        else:
            scrub_count = args.max_scrub_count
        if scrub_count > len(btrfs_mounts):
            scrub_count = len(btrfs_mounts)
        scrubber = issue_scrub_command(btrfs_mounts)
        for _ in range(scrub_count):
            scrubed_mounts = next(scrubber)
        print(f'Issued scrub to {GREEN}{scrubed_mounts}{RESET} mounts')
        scrub_start_time = time.time()
        #print(f'{GREEN}Scrub all issued!{RESET}')
        time.sleep(args.interval)

    
    while True:
        header = ["Mount", "Path", "FS Used", "w_err", "r_err", "bit_rot", "gen_err",
                            "scrub_status", "scrub_time", "scrub_rate", "scrubbed_data", "error_summary"]
        table = []
        running_scrubs = []
        if not btrfs_mounts:
            print(f"{RED}No Btrfs mounts found.{RESET}")
            return
        for mount in btrfs_mounts:
            mount_dir_name = mount.split("/")[-1]
            if not mount_dir_name:
                mount_dir_name = "/"
            # filesystem_show = execute_command(["btrfs", "filesystem", "show", mount])
            # device_stats = execute_command(["btrfs", "device", "stats", mount])
            # scrub_output = execute_command(["btrfs", "scrub", "status", device_path])
            filesystem_show, device_stats, scrub_output = execute_commands([
                ["btrfs", "filesystem", "show", mount],
                ["btrfs", "device", "stats", mount],
                ["btrfs", "scrub", "status", mount]
            ])
            #filesystem_show = multiCMD.run_command(["btrfs", "filesystem", "show", mount],quiet=True)
            uuid, fs_used, device_path = parse_show_info(filesystem_show)
            if uuid is None or fs_used is None or device_path is None:
                print(f"{RED}Could not fetch complete info for {mount}. Skipping...{RESET}")
                continue
            #device_stats = multiCMD.run_command(["btrfs", "device", "stats", mount],quiet=True)
            err_dict = parse_device_stats(device_stats)
            #scrub_output = multiCMD.run_command(["btrfs", "scrub", "status", device_path],quiet=True)
            scrub_data = parse_scrub_status(scrub_output)
            if scrub_data["scrub_status"] == "running":
                running_scrubs.append(mount)
            table.append([
                mount_dir_name,
                device_path,
                fs_used,
                color_error_count(err_dict['write_io_errs']),
                color_error_count(err_dict['read_io_errs']),
                color_error_count(err_dict['corruption_errs']),
                color_error_count(err_dict['generation_errs']),
                scrub_data["scrub_status"],
                scrub_data["scrub_time"],
                scrub_data["scrub_rate"],
                scrub_data["scrubbed_data"],
                scrub_data["error_summary"]
            ])

        print(multiCMD.pretty_format_table(table,header = header))


        if not args.scrub:
            break
        # issue scrub command to next mount if there are less than max_scrub_count scrubs running
        if len(running_scrubs) < scrub_count and time.time() - scrub_start_time > args.scrub_command_lockout and len(scrubed_mounts) < len(btrfs_mounts):
            scrubed_mounts = next(scrubber)
            # print(f'Issued scrub to {GREEN}{scrubed_mounts}{RESET} mounts')
            print(f"{GREEN}Scrubed issued to {scrubed_mounts}.{RESET}")
            scrub_start_time = time.time()

        if len(running_scrubs) == 0 and time.time() - scrub_start_time > args.scrub_command_lockout:
            print(f"{GREEN}All Scrubs finished.{RESET}")
            break

        time.sleep(args.interval)

if __name__ == "__main__":
    main()

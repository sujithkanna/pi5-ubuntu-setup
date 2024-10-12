import os
import subprocess

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.stderr}")
        return None

def list_partitions():
    """List all available partitions using lsblk and return a list of them."""
    command = "sudo lsblk -o NAME,SIZE,FSTYPE | sed 's/^[├└─]*//' | grep -E '^sd[a-z]+[0-9]+.*'"
    partitions = run_command(command)
    partition_list = []
    
    if partitions:
        print("Available partitions:\n")
        for i, line in enumerate(partitions.splitlines(), 1):
            # List partition details and save to partition_list
            print(f"{i}. {line}")
            partition_list.append(line.split()[0])  # Save partition name like sda1, sdb1
    else:
        print("No partitions found.")
    
    return partition_list

def get_partition_choice(partition_list):
    """Ask the user to input the number of the partition they want to mount."""
    while True:
        try:
            choice = int(input("\nEnter the number of the partition you want to mount: "))
            if 1 <= choice <= len(partition_list):
                return f"/dev/{partition_list[choice - 1]}"  # Return the partition name
            else:
                print(f"Invalid choice. Please choose a number between 1 and {len(partition_list)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def create_mount_point():
    """Create a directory to mount the partition."""
    mount_point = input("\nEnter the mount point directory (e.g., /mnt/mydisk): ").strip()
    if not os.path.exists(mount_point):
        os.makedirs(mount_point)
    return mount_point

def get_mount_info():
    """Get current mount points from /etc/mtab."""
    mount_info = {}
    with open('/etc/mtab', 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                device = parts[0]
                mount_point = parts[1]
                mount_info[device] = mount_point
    return mount_info

def remount_partition(device, new_mount_point):
    """Remount the partition to the new mount point."""
    # Check if the partition is already mounted somewhere else
    mount_info = get_mount_info()
    if device in mount_info:
        current_mount = mount_info[device]
        print(f"Partition {device} is already mounted at {current_mount}.")
        
        # Unmount the partition from the current mount point
        print(f"Unmounting {device} from {current_mount}...")
        run_command(f"sudo umount {current_mount}")
        
        # Now, mount it to the new directory
        print(f"Mounting {device} to {new_mount_point}...")
        run_command(f"sudo mount {device} {new_mount_point}")
        
        print(f"Partition {device} is now mounted at {new_mount_point}.")
    else:
        print(f"Partition {device} is not mounted. Mounting to {new_mount_point}...")
        run_command(f"sudo mount {device} {new_mount_point}")
        print(f"Partition {device} is mounted at {new_mount_point}.")

def mount_partition(partition, mount_point):
    """Mount the chosen partition to the specified mount point."""
    command = f"sudo mount {partition} {mount_point}"
    result = run_command(command)
    if result is None:
        print(f"Failed to mount {partition} to {mount_point}")
    else:
        print(f"Mounted {partition} to {mount_point}")

def get_uuid(partition):
    """Get the UUID of the partition."""
    command = f"sudo blkid {partition}"
    output = run_command(command)
    if output:
        uuid = output.split('UUID="')[1].split('"')[0]
        return uuid
    else:
        print(f"Could not retrieve UUID for {partition}")
        return None

def add_to_fstab(uuid, mount_point, filesystem):
    """Add the partition entry to /etc/fstab for automatic mounting. If an entry exists, remove and add it again."""
    # Prepare the new fstab entry
    fstab_entry = f"UUID={uuid} {mount_point} {filesystem} defaults 0 2\n"
    
    try:
        # Read the current contents of /etc/fstab
        with open("/etc/fstab", "r") as fstab_file:
            lines = fstab_file.readlines()
        
        # Remove any existing entries for the given UUID
        with open("/etc/fstab", "w") as fstab_file:
            for line in lines:
                if f"UUID={uuid}" not in line:
                    fstab_file.write(line)
        
        # Append the new entry
        with open("/etc/fstab", "a") as fstab_file:
            fstab_file.write(fstab_entry)
        
        print(f"Successfully added to /etc/fstab:\n{fstab_entry}")
    
    except Exception as e:
        print(f"Error writing to /etc/fstab: {e}")

def main():
    # Step 1: List available partitions
    partition_list = list_partitions()

    if not partition_list:
        return

    # Step 2: Get the chosen partition from the user
    partition = get_partition_choice(partition_list)

    # Step 3: Create the mount point directory
    mount_point = create_mount_point()

    # Step 4: Remount the partition (if already mounted) or mount it
    remount_partition(partition, mount_point)

    # Step 5: Get the UUID of the partition
    uuid = get_uuid(partition)
    
    if uuid:
        # Step 6: Determine the filesystem type
        filesystem = input("\nEnter the filesystem type (e.g., ext4, ntfs): ").strip()

        # Step 7: Add the partition to /etc/fstab
        add_to_fstab(uuid, mount_point, filesystem)

if __name__ == "__main__":
    main()

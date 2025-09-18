import time
import logging
import random # Used to simulate a random error for demonstration

# Set up basic logging configuration to output to the console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def simulate_wipe(drive_id, drive_type, drives_data):
    """
    Simulates a secure data wipe based on the drive's type.
    It updates the status and progress of the drive in the provided data list.
    """
    # Find the drive in the data list
    target_drive = next((drive for drive in drives_data if drive['id'] == drive_id), None)
    
    if not target_drive:
        logging.error(f"Error: Drive with ID '{drive_id}' not found.")
        return

    # Simulate an occasional error for testing the 'Error' state
    if random.random() < 0.1: # 10% chance of a simulated failure
        target_drive['status'] = "Error"
        target_drive['error_message'] = "Simulated write error during process."
        logging.error(f"Simulated failure for {target_drive['model']}.")
        return

    logging.info(f"Starting wipe simulation for {target_drive['model']} ({drive_type}).")
    target_drive['status'] = "Wiping in progress"
    target_drive['progress_percentage'] = 0

    if drive_type == "HDD":
        # Simulate a slower, multi-pass overwrite process
        for i in range(1, 11):
            progress = i * 10
            target_drive['progress_percentage'] = progress
            logging.info(f"Wiping {drive_id}: {progress}% complete.")
            time.sleep(0.5) # Simulate time delay

    elif drive_type in ["SSD", "NVMe"]:
        # Simulate a much faster Secure Erase or Crypto Erase
        logging.info("Using a fast Secure Erase simulation for SSD/NVMe.")
        time.sleep(1) # A small delay to show an action is taking place
        target_drive['progress_percentage'] = 100
        logging.info(f"Wiping {drive_id}: 100% complete.")

    # Mark the drive as wiped upon completion
    target_drive['status'] = "Wiped"
    del target_drive['progress_percentage'] # Clean up the progress indicator
    target_drive['is_wipeable'] = False # A wiped drive is no longer wipeable
    logging.info(f"Wipe simulation completed successfully for {target_drive['model']}.")
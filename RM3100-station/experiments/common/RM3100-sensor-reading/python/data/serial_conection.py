from datetime import datetime
import time

import serial

from ..utils import create_new_file

def is_data_line(camp: list[str]):
    """
    True if the line has exactly 4 integers: t_us, Xc, Yc, Zc
    """
    if len(camp) != 4:
        return False
    try:
        [int(c) for c in camp]
    except ValueError:
        return False
    return True


def conect_mc(cfg: dict, paths: dict, logging_info) :
    """
    Conect with port and save data
    """
    port = cfg["serial_config"]["port"]
    monitor_speed = cfg["serial_config"]["monitor_speed"]
    len_data = cfg["serial_config"]["len_data"]
    cycle_count = cfg["cycle_count"]
    rm3100_address = cfg["RM3100_address"]
    debug_mode = cfg["logging"]["debug_mode"]

    name_file =  datetime.now().strftime("rm3100_%Y%m%d_%H-%M-%S.txt")
    save_dir = create_new_file(paths, "raw_file", f"cc_{cycle_count}")
    save_file = save_dir / name_file

    n = 0
    cc_ok = cycle_count is None
    cc_verified = False


    with serial.Serial(port = port, baudrate = monitor_speed, timeout = 1) as ser, open(save_file, "w", newline = "", buffering = 1) as f:
        if cycle_count is not None:
            time.sleep(2)
            # Startup messages already in the buffer (REVID, TMRC, ...) are saved before the CC request;
            # the initial Cycle Count (initialCC) and the data lines are discarded
            while ser.in_waiting:
                line = ser.readline().decode("ascii", errors = "replace").strip()
                if line and not is_data_line(line.split(",")) and not line.startswith("Cycle Count"):
                    f.write(f"# {line}\n")
                    logging_info(debug_mode, msg = line)
            ser.write(f"CC={cycle_count}\n".encode("ascii"))

        try:
            while True:
                line = ser.readline().decode("ascii", errors = "replace").strip()
                if not line:
                    continue

                if is_data_line(line.split(",")):
                    if cc_ok:
                        if n == 0:
                            f.write(f"# Date = {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            cc_status = "verified" if cc_verified else "not verified"
                            f.write(f"# Cycle Count = {cycle_count} ({cc_status})" + " "*5 + f"RM3100 Address = 0x{rm3100_address:02X}\n")
                            f.write("# This data corresponds to raw format (LSB) data from the RM3100 sensor\n")
                            f.write("# " + "="*40 + "\n")
                            f.write("t_us,Xc,Yc,Zc\n")
                        f.write(line + "\n")
                        n += 1
                        if len_data is not None and n >= len_data:
                            break

                else:
                    if not cc_ok and (line.startswith("Cycle Count") or line == "Invalid CC"):
                        # Firmware answer to the CC request: compared with the requested value, not written as a comment
                        cc_ok = True
                        cc_verified = line == f"Cycle Count = {cycle_count}"
                        logging_info(debug_mode, msg = f"{line} ({'verified' if cc_verified else 'not verified'})")
                        continue
                    f.write(f"# {line}\n")
                    logging_info(debug_mode, msg = line)

        except KeyboardInterrupt:
            pass
        f.write(f"# Total data = {n}\n")

    logging_info(debug_mode, msg = f"{n} samples stored in {save_file}")
import serial
import time
import json

# Configuration of COM-port
COM_PORT = "COM5"   # Change to the used port
BAUDRATE = 9600     # Change to coorect baudrate
OUTPUT_FILE = "elapsed_time.json"

def write_json(filename, elapsed):
    data = {"elapsed_time": [ {"time": f"{elapsed:.2f}" } ] }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def parse_c1_time(line: str) -> float | None:
    """
    Extracting of time from c1-signaling.
    Ex: '0006 c1     00005.6200 00' -> 5.62
    """
    parts = line.split()
    for p in parts:
        try:
            return float(p)
        except ValueError:
            continue
    return None

def main():
    ser = serial.Serial(COM_PORT, BAUDRATE, timeout=1)
    running = False
    start_time = None

    try:
        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if not line:
                continue

            print("Received:", line)

            # Start of race
            if "C0M" in line and not running:
                start_time = time.time()
                running = True
                print("Startsignal received")

                # Update jSON-file until Stop
                while running:
                    elapsed = time.time() - start_time
                    write_json(OUTPUT_FILE, elapsed)
                    time.sleep(0.1) #Interval to update

                    # Search for Finishsignal
                    if ser.in_waiting:
                        stop_line = ser.readline().decode(errors="ignore").strip()
                        if "c1" in stop_line.lower():
                            stop_val = parse_c1_time(stop_line)
                            running = False
                            if stop_val is not None:
                                write_json(OUTPUT_FILE, stop_val)
                            else:
                                elapsed = time.time() - start_time
                                write_json(OUTPUT_FILE, elapsed)
                            print("Finish received, waiting for new start...")
                            print(stop_val)
                            break

    except KeyboardInterrupt:
        print("Closing manually...")
    finally:
        ser.close()

if __name__ == "__main__":
    main()

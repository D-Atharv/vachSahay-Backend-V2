# main.py
import sys
from audio_processor import process_audio

def main1():
    if len(sys.argv) != 3:
        print("Usage: main1.py <input_file_path> <output_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    process_audio(input_file_path, output_file_path)


if __name__ == "__main__":
    main1()
import subprocess
import threading
from queue import Queue, Empty

class ShellExecutor:
    def __init__(self):
        self.process = subprocess.Popen(
            '/bin/bash',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.output_queue = Queue()
        self.read_event = threading.Event()
        self.delimiter = "___COMMAND_COMPLETE___"

        self.stdout_thread = threading.Thread(target=self.reader_thread, args=(self.process.stdout, self.output_queue.put))
        self.stderr_thread = threading.Thread(target=self.reader_thread, args=(self.process.stderr, self.output_queue.put))

        self.stdout_thread.start()
        self.stderr_thread.start()

    def reader_thread(self, pipe, callback):
        for line in pipe:
            callback(line)
            if self.delimiter in line:
                self.read_event.set()

    def execute(self, cmd):
        self.read_event.clear()  # Reset the event
        if not cmd.endswith('\n'):
            cmd += '\n'
        full_cmd = cmd + f"echo {self.delimiter}\n"
        self.process.stdin.write(full_cmd)
        self.process.stdin.flush()

        # Wait for the reader_thread to signal that it's done reading the output
        self.read_event.wait()

    def get_output(self):
        lines = []
        while not self.output_queue.empty():
            line = self.output_queue.get()
            if self.delimiter in line:
                continue  # Exclude the delimiter from the returned output
            lines.append(line)

        if len(lines) > 50:
            return ''.join(["FIRST 50 LINES OF OUTPUT ONLY"] + lines[0:50])
        else:
            return ''.join(lines)

    def close(self):
        self.process.terminate()
        self.stdout_thread.join()
        self.stderr_thread.join()

shell = ShellExecutor()

def execute_command_and_get_output(command):
    print("executing command:", command)
    shell.execute(command)
    out = shell.get_output()
    print("output:", out)
    return out

# Example Usage:
if __name__ == '__main__':
    shell = ShellExecutor()

    while True:
        # Let's say this command is what your AI or main module wants to run:
        shell.execute(input())

        # Collect the output:
        print(shell.get_output())

    shell.close()

from typing import List
import threading
import time
import subprocess
import os
import signal
import logging


class ClientThread(threading.Thread):
    """
    Thread representing a client
    """

    def __init__(self, commands: List[str], time_step_len_seconds: float) -> None:
        """
        Initializes the client thread

        :param commands: the sequence of commands that the client will execute
        :param time_step_len_seconds: the length of a time-step in seconds
        """
        threading.Thread.__init__(self)
        self.commands = commands
        self.time_step_len_seconds = time_step_len_seconds
        self.daemon = True

    def run(self) -> None:
        """
        The main function of the client. It executes a sequence of commands and then terminates

        :return: None
        """
        for cmd in self.commands:
            p = None
            try:
                # start_new_session=True creates a new process group, allowing us to kill the shell + children
                p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                     shell=True, start_new_session=True)

                # Wait for command to finish with a hard timeout
                p.communicate(timeout=15)

            except subprocess.TimeoutExpired:
                # logging.warning(f"[Client] Command timed out: {cmd}. Killing process group {p.pid}.")
                if p:
                    try:
                        # Kill the entire process group (shell + commands)
                        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                    except (ProcessLookupError, OSError):
                        pass  # Process already died
            except Exception as e:
                # logging.error(f"[Client] Error executing command {cmd}: {e}")
                if p:
                    try:
                        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                    except:
                        pass
            finally:
                # Avoid zombie processes
                if p:
                    try:
                        p.wait(timeout=5)
                    except Exception:
                        try:
                            p.kill()
                            p.wait()
                        except:
                            pass

            time.sleep(self.time_step_len_seconds)

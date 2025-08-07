import threading
import multiprocessing
from facial_expression import facial_expression_monitoring




if __name__ == "__main__":
    # multiprocessing.set_start_method('spawn')
    facial_expression_thread = threading.Thread(target=facial_expression_monitoring, daemon=True)
    facial_expression_thread.start()


    try:
        while facial_expression_thread.is_alive():
            pass            
    except KeyboardInterrupt:
        print("Interrupted. Exiting...")

    print("Program ended.")
import threading

from facial_expression import facial_expression_monitoring




if __name__ == "__main__":
    facial_expression_thread = threading.Thread(target=facial_expression_monitoring, daemon=True)
    facial_expression_thread.start()
    facial_expression_thread.join()


    try:
        while facial_expression_thread.is_alive():
            pass            
    except KeyboardInterrupt:
        print("Interrupted. Exiting...")

    print("Program ended.")
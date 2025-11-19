from time import perf_counter

class SimpleTimer:
    def __init__(self, name: str = None, decimal: int = 4):
        self.name: str = name
        self.is_running: bool = False
        
        self.__start_time: float = None
        self.__time_buffer: float = 0.
        
        self.__decimal: int = decimal
    
    @property
    def time(self) -> float:
        if self.is_running:
            return self.__time_buffer + perf_counter() - self.__start_time
        else:
            return self.__time_buffer
        
    def start(self) -> None:
        if not self.is_running:
            self.is_running = True
            self.__start_time = perf_counter()

    def stop(self) -> float:
        stop_time = perf_counter()
        if self.is_running:
            self.is_running = False
            self.__time_buffer += stop_time - self.__start_time
        return self.time

    def reset(self) -> None:
        self.is_running: bool = False
        
        self.__start_time: float = None
        self.__time_buffer: float = 0.

    def __str__(self) -> str:
        current_status: str = "Running" if self.is_running else "Stopped"
        name: str  = "Timer" if self.name is None else self.name
        return f"{name} ({current_status}): {self.time:.{self.__decimal}f}s"
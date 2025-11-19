from .SimpleTimer import SimpleTimer

class AdvancedTimer(SimpleTimer):
    def __init__(self, name: str = None, decimal: int = 4, print_result: bool = False, return_result: bool = False):
        super().__init__(name=name, decimal=decimal)
        
        self.__print_result: bool = print_result
        self.__return_result: bool = return_result
        
    
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        if self.__print_result:
            print(self)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            self.start()
            try:
                ret_value = func(*args, **kwargs)
                return self.time, ret_value if self.__return_result else ret_value
            finally:
                self.stop()
                if self.__print_result:
                    print(self)
        return wrapper
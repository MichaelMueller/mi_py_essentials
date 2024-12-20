import traceback, sys, time, tempfile, asyncio, shutil,inspect

class Test:
    
    def __init__(self, parent:"Test") -> None:
        self._parent = parent
        self._start_time:int = time.time()    
        self._tmp_dir = None
            
    async def _exec(self) -> bool|None:
        raise NotImplementedError()
    
    async def exec(self) -> bool:
        result = False
        try:
            print(f'****** {self.name()} - STARTING')
            result = await self._exec()
            if result == None:
                result = True
            print(f'****** {self.name()} - {"PASSED" if result == True else "FAILED"}')
        except Exception as e:
            print(f'****** {self.name()} - FATALLY FAILED: {e}')
            traceback.print_exc()
        finally:
            await self._tidy_up()
        
        if self._parent == None:
            print(f'****** TESTS {"PASSED" if result == True else "FAILED"} - EXITING NOW!')
                
            sys.exit( 0 if result == True else 1)
        return result
    
    async def _tidy_up(self) -> None:
        if self._tmp_dir:
            loop = asyncio.get_event_loop()            
            self._print(f'Deleting tmp dir "{self._tmp_dir}"')
            await loop.run_in_executor(None, lambda: shutil.rmtree(self._tmp_dir))
        
    def name( self ) -> str:
        return self.__class__.__name__
    
    def _print(self, msg):
        print(f'****** {self.name()} - {msg}')
    
    
    async def _expect_exception( self, func:callable, func_description:str, exception_class:type ) -> None:
        unexcepted_exception = None
        
        try:
            await func() if inspect.iscoroutinefunction(func) else func()         
        except Exception as e:
            if isinstance(e, exception_class):                
                print(f'****** {self.name()} - Expected exception PASSED: {exception_class.__name__} when {func_description}')
            else:
                unexcepted_exception = e
        
        if unexcepted_exception is not None:
            raise unexcepted_exception
    
    def _check( self, condition:bool, description:str, assertion:bool=True ) -> "Test":
        if condition == True:
            print(f'****** {self.name()} - PASSED: {description}')
        else:            
            if assertion:
                raise AssertionError(description)
            else:                
                print(f'****** {self.name()} - FAILED: {description}')
                
        return self

    def _timer_start(self) -> "Test":
        self._print("STARTING TIMER")
        self._start_time = time.time()
        return 
    
    def _timer_end(self) -> int:
        end_time = time.time()  # End time
        self._print("STOPPED TIMER")
        execution_time = end_time - self._start_time
        self._start_time = time.time()
        return execution_time
    
    def _timer_check(self, accetaple_time_in_seconds:float, assertion:bool=True ) -> "Test":
        exec_time = self._timer_end()
        
        self._check( exec_time <= accetaple_time_in_seconds, f'exec_time <= {accetaple_time_in_seconds} seconds, got {exec_time} seconds', assertion=assertion )
        
        return self
        
    async def tmp_dir(self) -> str:
        if not self._tmp_dir:    
            loop = asyncio.get_event_loop()
            # Run the synchronous tempfile.mkdtemp in a thread pool to make it non-blocking
            self._tmp_dir = await loop.run_in_executor(None, tempfile.mkdtemp)
            self._print(f'Created tmp dir "{self._tmp_dir}"')
        return self._tmp_dir
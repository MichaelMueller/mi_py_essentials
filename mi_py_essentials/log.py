import logging

class Log:    

    def set_log_level( log_level:str ) -> None:
        # Set up basic logging
        log_level = getattr(logging, log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        
    def add_filter( log_filter:str ) -> None:
        # Set up regex!
        if log_filter != None:
            class GlobalRegexFilter(logging.Filter):
                def __init__(self, pattern):
                    super().__init__()
                    self.pattern = re.compile(pattern)

                def filter(self, record):
                    # Suppress log messages that match the regex
                    return not self.pattern.search(record.getMessage())            
            logging.getLogger().addFilter(GlobalRegexFilter(log_filter))
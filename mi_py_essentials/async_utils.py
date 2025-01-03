import aiofiles, json, logging, tempfile, asyncio

class AsyncUtils:    
    def __init__(self):
        pass
    
    async def read(self, file_path:str) -> str:
        """Reads a JSON file asynchronously."""
        async with aiofiles.open(file_path, mode='r') as file:
            return await file.read()

    async def write(self, file_path, data:str) -> None:
        """Writes data to a JSON file asynchronously."""
        async with aiofiles.open(file_path, mode='w') as file:
            logging.getLogger(__name__).debug(f'Writing to file {file_path}')
            await file.write(data)
            
    async def read_json(self, file_path):
        """Reads a JSON file asynchronously."""
        return json.loads( await self.read( file_path ) )

    async def write_json(self, file_path, data, indent=2):
        await self.write( file_path, json.dumps(data, indent=indent) )
            
    async def create_temp_folder(self) -> "str":
        # Use tempfile.TemporaryDirectory for safe temporary folder creation
        loop = asyncio.get_event_loop()
        temp_dir = await loop.run_in_executor(None, tempfile.TemporaryDirectory)
        return temp_dir.name
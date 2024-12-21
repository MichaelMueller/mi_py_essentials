import aiofiles, json, logging, tempfile, asyncio

class AsyncUtils:    
    async def read(file_path:str) -> str:
        """Reads a JSON file asynchronously."""
        async with aiofiles.open(file_path, mode='r') as file:
            return await file.read()

    async def write(file_path, data:str) -> None:
        """Writes data to a JSON file asynchronously."""
        async with aiofiles.open(file_path, mode='w') as file:
            logging.getLogger(__name__).debug(f'Writing to file {file_path}')
            await file.write(data)
            
    async def read_json(file_path):
        """Reads a JSON file asynchronously."""
        return json.loads( await AsyncUtils.read( file_path ) )

    async def write_json(file_path, data, indent=2):
        await AsyncUtils.write( file_path, json.dumps(data, indent=indent) )
            
    async def create_temp_folder():
        # Use tempfile.TemporaryDirectory for safe temporary folder creation
        loop = asyncio.get_event_loop()
        temp_dir = await loop.run_in_executor(None, tempfile.TemporaryDirectory)
        return temp_dir
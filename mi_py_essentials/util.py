import aiofiles, json, logging

class Util:    

    async def read_json(file_path):
        """Reads a JSON file asynchronously."""
        async with aiofiles.open(file_path, mode='r') as file:
            content = await file.read()
            return json.loads(content)

    async def write_json(file_path, data):
        """Writes data to a JSON file asynchronously."""
        async with aiofiles.open(file_path, mode='w') as file:
            content = json.dumps(data, indent=4)
            logging.getLogger(__name__).debug(f'Writing json to file {file_path}')
            await file.write(content)
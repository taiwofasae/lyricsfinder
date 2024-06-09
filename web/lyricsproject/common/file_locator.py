from common import file, s3, log
import os

def extract_file_protocol(filepath):
    protocol = None
    
    splits = filepath.split('://')
    if len(splits) > 1:
        protocol = splits[0].lower()
        filepath = splits[1]

    return protocol, filepath

class FileLocator:

    def __init__(self, source, temp_path = None) -> None:
        if not source:
            log.error("FileLocator: source path not provided.")
            raise ValueError("FileLocator.source not given")
        protocol, filepath = extract_file_protocol(source)
        self.source = filepath
        self.protocol = protocol
        self.temp_source = temp_path or filepath

        if temp_path:
            log.info("temp_path provided. Saving to temp...")
            if self.is_from_s3():
                self.temp_source = os.path.join('s3', self.temp_source)

            # save to temporary path
            file.make_directory_from_filepath(self.temp_source)
            if self.is_file_protocol():
                file.copy(self.source, self.temp_source)
            elif self.is_from_s3():
                s3.download_file_to(self.source, file.get_full_path(self.temp_source))
        elif self.is_from_s3():
            log.warn("No temporary path provided for s3 source.")
        

    def load(self, *args, **kwargs):
        
        if self.temp_source:
            log.info("loading from temporary source")
            with open(file.get_full_path(self.temp_source)) as f:
                return f.read(*args, **kwargs)
        
        # then read from source
        if self.is_from_s3():
            return s3.download_file(self.source, json_deserialize=False)
        
        if self.is_file_protocol():
            return file.download_file(file_name=self.source, json_deserialize=False)

    def full_temp_path(self):
        return file.get_full_path(self.temp_source)
    
    def full_source_path(self):
        if self.is_file_protocol():
            return file.get_full_path(self.source)
        return self.source
    
    def is_from_s3(self):
        return self.protocol == 's3'
    
    def is_file_protocol(self):
        return self.protocol == 'file'
    
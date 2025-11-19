import os
import pickle

from cryptography.fernet import Fernet

class SimpleFernet:
    """A wrapper around the `fernet` module from the `cryptography` package
    designed to simplify the process of using Fernet.
    """

    def __init__(self, key_environment_variable: str = None):
        """Initializes an instance of SimpleFernet.
        
        ## Arguments
        - `key_environment_variable`: A string representing the name of an
        environment variable that contains a Fernet key.
        
        ## Notes
        - It is assumed that you have already created a Fernet key and stored
        its value in an environment variable. This is due to limitations related
        to setting environment variables with Python code.
        """
        self.key_environment_variable = key_environment_variable

        if self.key_environment_variable is None:
            raise ValueError('key_environment_variable is not set. Please provide a valid environment variable name.')
        elif self.key_environment_variable is not None and os.getenv(key=self.key_environment_variable) is None:
            # TODO: Consider adding logic to set the environment variable such that it persists.
            raise ValueError(f'The environment variable "{self.key_environment_variable}" is not set. Please set its value to a Fernet key.')
        else:
            try:
                Fernet(key=os.getenv(key=self.key_environment_variable))
            except:
                raise ValueError(f'The Fernet key in the environment variable "{self.key_environment_variable}" is invalid. Please confirm the value is a valid Fernet key and try again.')
    
    def encrypt(self, data) -> bytes | None:
        """Converts the provided data to bytes and encrypts it using Fernet.
        
        ## Arguments
        - `data`: The data to be encrypted.
        
        ## Returns
        A `bytes` object representing the encrypted data or `None` (if the
        encryption operation failed for some reason).
        """
        # Declare and initialize an object to represent the encrypted data. This
        # variable is initialized to `None` in case there is some issue during
        # the encryption process that prevents the data from being encrypted as
        # expected.
        encrypted_data: bytes | None = None
        
        # Serialize the provided data to a byte stream (`bytes`).
        data_bytes: bytes = pickle.dumps(obj=data)
        
        # Encrypt the serialized data.
        encrypted_data = Fernet(key=os.getenv(key=self.key_environment_variable)).encrypt(data=data_bytes)
        
        return encrypted_data
    
    def decrypt(self, encrypted_data: bytes | str):
        """Decrypts the provided encrypted data using Fernet.
        
        ## Arguments
        - `encrypted_data`: A `bytes` or `str` value representing the data to
        decrypt with Fernet.
        
        ## Returns
        The decrypted data or `None` (if the decryption operation failed for
        some reason).
        
        ## Notes
        - The value passed in as `encrypted_data` must be of type `bytes` or
        `str`. If not, a `TypeError` will be raised.
        """
        # Declare and initialize a variable to represent the decrypted data.
        # This variable is initialized to `None` in case there is some issue
        # during the decryption process that prevents the encrypted data from
        # being decrypted as expected.
        decrypted_data: bytes | None = None
        
        # Declare and initialize a variable representing a "working" version of
        # the encrypted data passed in as `encrypted_data`. This is used to
        # establish a version of `encrypted_data` that can be manipulated if
        # necessary to support the decryption effort.
        encrypted_data_working = encrypted_data
        
        # Check the type of the encrypted data. If it is bytes or str, proceed
        # to decrypt the data. If the type is not bytes or str, raise a
        # TypeError.
        if type(encrypted_data_working) in [bytes, str]:
            # If the encrypted data was passed in as a string, encode it to
            # bytes before attempting to decrypt.
            if type(encrypted_data_working) is str:
                encrypted_data_working = encrypted_data_working.encode()
            
            # Decrypt the data using Fernet.
            decrypted_data = Fernet(key=os.getenv(key=self.key_environment_variable)).decrypt(token=encrypted_data_working)
            
            # Deserialize the data with pickle. This should return the data to
            # its original, pre-encryption type.
            decrypted_data = pickle.loads(decrypted_data)
        else:
            raise TypeError('encrypted_data must be either bytes or str.')
            
        return decrypted_data
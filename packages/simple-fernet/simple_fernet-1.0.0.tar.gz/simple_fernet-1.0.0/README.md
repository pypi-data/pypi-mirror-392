# simple-fernet

A Python package that streamlines the process of encrypting and decrypting data with [Fernet](https://pypi.org/project/cryptography).

This package leverages user-specified Fernet keys stored in environment variables to simplify the process of encrypting and decrypting data with that key in Fernet. In addition, `simple-fernet` minimizes the amount of time that Fernet keys are held in-memory by only retrieving and using these keys when they're needed to encrypt or decrypt data.

## Limitation Related to Environment Variables and Python

Use of `simple-fernet` requires that Fernet keys are both generated and stored in environment variables manually (before `simple-fernet` can be used). This is due to limitations around interfacing with system environment variables through Python, especially without requesting or providing privileged access.

Package maintainers are investigating ways to eliminate the need for these manual steps and will implement a solution if found. There are plans to develop a small companion tool to aid in the process of generating Fernet keys while this research is conducted.

For guidance on how to complete these manual steps (if you do not already have a Fernet key stored in environment variables), see the Quick Start below.

## Features

- Initialize instance of `SimpleFernet`, enabling encryption and decryption operations using a Fernet key stored in a user-provided environment variable.
- Encrypt data.
- Decrypt data.

## Ideas for a Future Release

- Add support for generating Fernet keys and storing them in system environment variables.

## Quick Start

This quick start will guide you through the process of using `simple-fernet` in your Python projects.

This guide assumes the following:
- You have installed Python on the system where you intend to use `simple-fernet`.
- You have not yet installed [the `cryptography` Python package](https://pypi.org/project/cryptography).
- You have not yet generated a Fernet key.
- You have not yet added a Fernet key to the system's environment variables.

With these assumptions in mind, this guide includes steps to generate a Fernet key and store it in environment variables for `simple-fernet` to use. If you have already generated a Fernet key and stored it in an environment variable, feel free to skip ahead in the guide.

If you have any feedback or suggestions to improve this guide, please don't hesitate to [open an issue on GitHub](https://github.com/darkroastcreative/simple-fernet/issues/new/choose)!

### macOS and Linux

Content coming soon!

### Windows

1. Install [the `cryptography` Python package](https://pypi.org/project/cryptography). On most systems, you can use `python -m pip install cryptography` to accomplish this.
2. Generate a Fernet key using the `fernet` module of the `cryptography` Python package. You can copy and paste the "Generate Fernet Key" script provided in this README's appendix into a new `.py` file and run it to do this quickly.
3. Copy the generated Fernet key.
4. Open the Windows Start Menu, search for "Edit the system environment variables," and select the matching search result.
5. In the System Properties window that opens, click the "Environment Variables" button.
6. Click the "New" button in the "System variables" section.
7. In the New System Variable window that appears, give the new environment variable a name and paste the Fernet key you generated in Step 2 into the "Variable value" field.
8. Click "OK" until all three windows that you opened to edit the system's environment variables are closed.
9. Install [the `simple-fernet` Python package]() using a command like `python -m pip install simple-fernet`.
10. In your Python code (that you want to use `simple-fernet` in), add the following import statement: `from simple_fernet import SimpleFernet`
11. Initialize an instance of the `SimpleFernet` class, passing in the name of the environment variable you created as an argument (e.g., `sf = SimpleFernet('TEST_FERNET_KEY)`).
12. Call the `encrypt()` and `decrypt()` methods of your `SimpleFernet` instance as needed to encrypt and decrypt data with the Fernet key you created.


## `SimpleFernet` Class

The `SimpleFernet` class is the heart of `simple-fernet`. Instances of the `SimpleFernet` class are used to facilitate data encryption and decryption with a pre-defined Fernet key (stored in an environment variable).

### Initializer

The `SimpleFernet` initializer instantiates an instance of the `SimpleFernet` class and returns it so it can be used to encrypt and decrypt data.

#### Arguments

- `key_environment_variable`: A string representing the name of an environment variable that contains a Fernet key. Please note that the Fernet key must be generated outside of `simple-fernet` and stored in environment variables before `SimpleFernet` can use it (see above note on limitations of the package).

#### Returns

An initialized instance of the `SimpleFernet` class.

### `encrypt()` Method

Converts the provided data to `bytes`, encrypts it using Fernet, and returns the encrypted data as `bytes`.

#### Arguments

- `data`: The data to be encrypted.

#### Returns

A `bytes` object representing the encrypted data or `None` (if the encryption operation failed for some reason).

### `decrypt()` Method

Decrypts the provided encrypted data using Fernet and returns it.

#### Arguments

- `encrypted_data`: A `bytes` or `str` value representing the data to decrypt with Fernet.

#### Returns

The decrypted data or `None` (if the decryption operation failed for some reason).

#### Notes

- The value passed in as `encrypted_data` must be of type `bytes` or `str`. If not, a `TypeError` will be raised.

## Appendix

### Script: Generate Fernet Key

This script provides a quick and easy way to generate a Fernet key.

Please note that this script requires that [the `cryptography` Python package](https://pypi.org/project/cryptography) is installed in the environment where you run it.

When extracting the generated key, copy only the characters between `b'` and the closing single quote (`'`). For example, if this script prints `b'6D9q48iAPS87jrz8zp5fiGj7VBGCyS9TGvJJ08QhkQ8='`, only copy `6D9q48iAPS87jrz8zp5fiGj7VBGCyS9TGvJJ08QhkQ8=`.

```python
from cryptography.fernet import Fernet

print(Fernet.generate_key())
```

### Script: Sample of How to Use `simple-fernet` in Python Code

This script is an extremely simple example of how to use `simple-fernet` in your Python code.

In this script, the `simple-fernet` package is imported, an instance of `SimpleFernet` is initialized, a simple list is established, encrypted, and decrypted.

```python
from simple_fernet import SimpleFernet

sf = SimpleFernet(key_environment_variable='TEST_FERNET_KEY')

raw_data = ['Hello, world!', 67, {'Name': 'simple-fernet', 'isCool': True}]

print(f'Raw Data: {raw_data}')

encrypted_data = sf.encrypt(raw_data)

print(f'Encrypted Data: {encrypted_data}')

decrypted_data = sf.decrypt(encrypted_data)

print(f'Decrypted Data: {decrypted_data}')
```

import json
import ast # added for literal_eval
from encryption import encryptText, decryptText

# function to save passwords in json format as specified
def savePasswordsToFile(passwordsDictionary, masterPasswordValue):
    # create a dictionary to store encrypted passwords
    encrypted_passwords = {}
    for site_value, password_data in passwordsDictionary.items():
        # convert password data (dict) to a json string, then encrypt it
        # print(f"saving site: {site_value}, data: {password_data}") # debug
        password_data_str = json.dumps(password_data)
        encrypted_password_value = encryptText(password_data_str, masterPasswordValue)
        encrypted_passwords[site_value] = encrypted_password_value
    
    # write the encrypted dictionary to file as json
    with open('passwords.json', 'w') as f:
        json.dump(encrypted_passwords, f, indent=2)
    return True # indicate success

# function to load passwords from json format
def loadPasswordsFromFile(masterPasswordValue):
    # create empty dictionary for passwords
    passwords_dictionary = {}
    
    # try to open file
    try:
        with open('passwords.json', 'r') as f:
            encrypted_passwords = json.load(f)
    except FileNotFoundError:
        return passwords_dictionary
    except json.JSONDecodeError:
        # if json parsing fails, it might be an empty or malformed file, or old format
        # try to read as plain text and handle old format if possible
        try:
            with open('passwords.json', 'r') as f:
                content = f.read()
                if not content.strip(): # handle empty file case after decode error
                    return passwords_dictionary
                # for old, custom json format, it was structured like site:encrypted_pass
                # but the encrypted_pass value itself might be a string representation of a dict
                # from older versions that used str() instead of json.dumps()
                # if the JSONDecodeError occurred, it's likely not standard JSON.
                # for simplicity and safety, if json.load fails, we return empty dict for now
                # to avoid complex manual parsing of potentially mixed formats.
                # if persistent old data is expected, more robust parsing is needed here.
                print("json decode error, returning empty dict. content was:", content) # debug
                return passwords_dictionary
        except Exception as e:
            print(f"error reading file after json decode error: {e}") # debug
            return passwords_dictionary

    # go through each encrypted entry
    for site_value, encrypted_password_value in encrypted_passwords.items():
        try:
            # decrypt the password value
            decrypted_value = decryptText(encrypted_password_value, masterPasswordValue)
            # print(f"decrypted for {site_value}: {decrypted_value}") # debug
            
            # try to parse as new format (dict), fallback to old format (string)
            parsed_data = decrypted_value
            for _ in range(10): # try up to 10 unescape/parse attempts
                if isinstance(parsed_data, dict) and 'password' in parsed_data:
                    break # successfully parsed as a dict
                
                try:
                    # first, try to load as json directly
                    new_parsed_data = json.loads(parsed_data)
                    parsed_data = new_parsed_data
                except json.JSONDecodeError:
                    # if json fails, try unescaping and then literal_eval
                    try:
                        temp_value = parsed_data.encode().decode('unicode_escape')
                        # after unescaping, try json again
                        new_parsed_data = json.loads(temp_value)
                        parsed_data = new_parsed_data
                    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                        # if json still fails, or unescaping itself causes an error, try literal_eval
                        try:
                            # before literal_eval, remove any outer quotes if they exist
                            if temp_value.startswith(('"', "'")) and temp_value.endswith(('"', "'")):
                                temp_value = temp_value[1:-1]
                            new_parsed_data = ast.literal_eval(temp_value)
                            parsed_data = new_parsed_data
                        except (ValueError, SyntaxError):
                            # if all else fails, break the loop and keep the current parsed_data
                            break
                except Exception: # catch any other unexpected errors during parsing
                    break

            if isinstance(parsed_data, dict) and 'password' in parsed_data:
                passwords_dictionary[site_value] = parsed_data
            else:
                # if it's a valid json but not a dict with 'password', or still a string after attempts,
                # store the original decrypted string or the closest parsed value.
                passwords_dictionary[site_value] = parsed_data if isinstance(parsed_data, str) else decrypted_value
        except Exception as e:
            # print(f"decryption failed for {site_value}: {e}") # debug
            continue # skip if decryption fails
    
    # return the dictionary
    return passwords_dictionary
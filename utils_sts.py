#!/usr/bin/env python2

# Import AWS utils
from AWSUtils.utils_iam import *

# Import third-party packages
import boto


########################################
##### Helpers
########################################

def init_sts_session(profile_name, credentials_file = aws_credentials_file_no_mfa, mfa_code = None):
    save_no_mfa_credentials = False
    try:
        # Parse no-MFA config
        key_id, secret, mfa_serial, session_token = read_creds_from_aws_credentials_file(profile_name, credentials_file = credentials_file)
        if not key_id or not secret:
            # Parse normal config
            key_id, secret, mfa_serial, session_token = read_creds_from_aws_credentials_file(profile_name)
            if not key_id or not secret:
                print 'Error, could not find credentials for profile \'%s\'.' % profile_name
                return False
            else:
                save_no_mfa_credentials = True
        if not mfa_serial:
            # Prompt for MFA serial
            mfa_serial = prompt_4_mfa_serial()
            save_no_mfa_credentials = True
        if not mfa_code:
            # Prompt for MFA code
            mfa_code = prompt_4_mfa_code()
        # Fetch session token and set the duration to 8 hours
        sts_connection = boto.connect_sts(key_id, secret)
        sts_response = sts_connection.get_session_token(mfa_serial_number = mfa_serial, mfa_token = mfa_code, duration = 28800)
        if save_no_mfa_credentials:
            # Write long-lived credentials to the no-MFA config file
            write_creds_to_aws_credentials_file(profile_name, key_id = key_id, secret = secret, mfa_serial = mfa_serial, credentials_file = aws_credentials_file_no_mfa)
        # Write the new credentials to the config file
        write_creds_to_aws_credentials_file(profile_name, key_id = sts_response.access_key, secret = sts_response.secret_key, session_token = sts_response.session_token)
        # Success
        print 'Successfully configured the session token for profile \'%s\'.' % profile_name
        return True
    except Exception, e:
        printException(e)
        return False


########################################
##### STS-related arguments
########################################

parser.add_argument('--mfa_code',
                    dest='mfa_code',
                    default=[''],
                    nargs='+',
                    help='MFA code')

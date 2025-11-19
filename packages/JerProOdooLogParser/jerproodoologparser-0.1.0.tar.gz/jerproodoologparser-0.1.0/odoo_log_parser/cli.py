#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, odoo_log_parser, os, sys, importlib

def Main(exec_name, exec_argv):
    """
    Program entry-point - Parses the command line arguments and
    invokes corresponding semantics.
        exec_name   The bin name used to call the program.
        exec_argv   Array of program arguments to parse.
    """
    ####################################
    ### Cmdline config:
    parser = argparse.ArgumentParser(description='A program for parsing and resuming Odoo logs.')
    parser.add_argument('--odoolog', type=str,
        help=('Odoo logfile path.'))
    parser.add_argument('--echo-mode', type=str,
        help=('A comma-separated list of modes on how the log digest is to be echoed to the user.'))
    parser.add_argument('--list-echo-modes', action='store_const', const=True, default=False,
        help=('Just print-out a list of echo modes.'))
    parser.add_argument('--always-succeed', action='store_const', const=True, default=False,
        help=('Always return SUCCESS regardles of test failures.'))
    args = parser.parse_args(args=exec_argv)
    ####################################
    ## Implement echo mode listing:
    if args.list_echo_modes:
        eml = odoo_log_parser.EchoMode.get_echo_modes_list()
        print("=== Echo modes:")
        for emn in eml:
            print(emn)
        return 0
    ####################################
    ## Resume the logfile:
    with open(args.odoolog, "r") as logfilo:
        logparser = odoo_log_parser.OdooTestDigest(logfilo)
        digest = logparser.get_full_test_digest()
    ####################################
    ### Optionally parse and echo the digest:
    # Find out how to digest is to be printed:
    echo_mode_functions = list()
    if args.echo_mode:
        req_modes = args.echo_mode.split(',')
        for rm in req_modes:
            this_pi = odoo_log_parser.EchoMode.get_echo_plugin(rm)
            if this_pi is None:
                print(f"ERROR: Echo mode {repr(rm)} not found!")
                return -1
            echo_mode_functions.append( (rm, this_pi) )
    else:
        print("Hint: Use the --echo-mode flag to parse the log digest.")
    # Print the digest according to what was found out:
    for pmf in echo_mode_functions:
        to_print = (
              f"===============================\n"
            + f"== Echoing «{pmf[0]}»:\n"
            + f"===============================\n"
            + f"{pmf[1](digest)}" + "\n"
            )
        print( to_print )
    ### See if there are only sucesses, unless otherwise requested:
    if args.always_succeed:
        return 0
    else:
        all_success = True
        for dbreport in digest.values():
            if len(dbreport['tests_failing']) > 0:
                all_success = False
            if len(dbreport['tests_errors']) > 0:
                all_success = False
            if len(dbreport['setup_errors']) > 0:
                all_success = False
        ### Devise a proper return value in POSIX language:
        return 0 if all_success else 1

def entrypoint(): exit(Main(exec_name=sys.argv[0], exec_argv=sys.argv[1:]))

#!/usr/bin/python
#
# (C) 2012 by Pablo Neira Ayuso <pablo@netfilter.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This software has been sponsored by Sophos Astaro <http://www.sophos.com>
#

import sys
import os
import subprocess
import argparse

IPTABLES = "iptables"
IP6TABLES = "ip6tables"
EXTENSIONS_PATH = "extensions"


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


def print_error(filename, lineno, reason):
    print (filename + ": " + Colors.RED + "ERROR" +
           Colors.ENDC + ": line %d (%s)" % (lineno, reason))


def delete_rule(iptables, rule, filename, lineno, devnull):
    cmd = iptables + " -D " + rule
    ret = subprocess.call(cmd, stderr=devnull, shell=True)
    if ret == 1:
        reason = "cannot delete: " + iptables + " -I " + rule
        print_error(filename, lineno, reason)
        return -1

    return 0


def run_test(iptables, rule, rule_save, res, filename, lineno, devnull):
    ret = 0

    cmd = iptables + " -A " + rule
    ret = subprocess.call(cmd, stderr=devnull, shell=True)

    #
    # report failed test
    #
    if ret:
        if res == "OK":
            reason = "cannot load: " + cmd
            print_error(filename, lineno, reason)
            return -1
        else:
            # do not report this error
            return 0
    else:
        if res == "FAIL":
            reason = "should fail: " + cmd
            print_error(filename, lineno, reason)
            delete_rule(iptables, rule, filename, lineno, devnull)
            return -1

    matching = 0
    proc = subprocess.Popen(iptables + "-save", stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    #
    # check for segfaults
    #
    if proc.returncode == -11:
        reason = "iptables-save segfaults: " + cmd
        print_error(filename, lineno, reason)
        delete_rule(iptables, rule, filename, lineno, devnull)
        return -1

    matching = out.find(rule_save)
    if matching < 0:
        reason = "cannot find: " + iptables + " -I " + rule
        print_error(filename, lineno, reason)
        delete_rule(iptables, rule, filename, lineno, devnull)
        return -1

    return delete_rule(iptables, rule, filename, lineno, devnull)


def execute_cmd(external_cmd, devnull):
    subprocess.call(external_cmd, stderr=devnull, shell=True)


def run_test_file(filename):
    tests = 0
    passed = 0

    #
    # if this is not a test file, skip.
    #
    if filename[len(filename)-2:] != ".t":
        return 0, 0

    if filename.find("libipt_") > 0:
        iptables = IPTABLES
    elif filename.find("libip6t_") > 0:
        iptables = IP6TABLES
    elif filename.find("libxt_") > 0:
        iptables = IPTABLES
    else:
        # default to iptables if not known prefix
        iptables = IPTABLES

    f = open(filename)

    lineno = 0
    chain = ""
    table = ""
    external_cmd = ""
    total_test_passed = True

    # FIXME: better store standard error output in one log filename
    devnull = open("/dev/null", "w")

    for line in f:
        lineno = lineno + 1

        if line[0] == "#":
            continue

        if line[0] == ":":
            chain_array = line.rstrip()[1:].split(",")
            continue

        # external non-iptables invocation, executed as is.
        if line[0] == "!":
            external_cmd = line.rstrip()[1:]
            execute_cmd(external_cmd, devnull)
            continue

        if line[0] == "*":
            table = line.rstrip()[1:]
            continue

        if len(chain_array) == 0:
            print "broken test, missing chain, leaving"
            sys.exit()

        test_passed = True
        tests = tests + 1

        for chain in chain_array:

            item = line.split(";")
            if table == "":
                rule = chain + " " + item[0]
            else:
                rule = chain + " -t " + table + " " + item[0]

            if item[1] == "=":
                rule_save = chain + " " + item[0]
            else:
                rule_save = chain + " " + item[1]

            res = item[2].rstrip()

            ret = run_test(iptables, rule, rule_save,
                           res, filename, lineno, devnull)
            if ret < 0:
                test_passed = False
                total_test_passed = False
                break

        if test_passed:
            passed = passed + 1

    if total_test_passed:
        print filename + ": " + Colors.GREEN + "OK" + Colors.ENDC

    f.close()
    devnull.close()
    return tests, passed


def show_missing():
    '''
    Show the list of missing test files
    '''
    file_list = os.listdir(EXTENSIONS_PATH)
    testfiles = [i for i in file_list if i.endswith('.t')]
    libfiles = [i for i in file_list
                if i.startswith('lib') and i.endswith('.c')]

    def test_name(x):
        return x[0:-2] + '.t'
    missing = [test_name(i) for i in libfiles
               if not test_name(i) in testfiles]

    print '\n'.join(missing)


#
# main
#
def main():
    parser = argparse.ArgumentParser(description='Run iptables tests')
    parser.add_argument('filename', nargs='?',
                        metavar='path/to/file.t',
                        help='Run only this test')
    parser.add_argument('-m', '--missing', action='store_true',
                        help='Check for missing tests')
    args = parser.parse_args()

    #
    # show list of missing test files
    #
    if args.missing:
        show_missing()
        return

    if os.getuid() != 0:
        print "You need to be root to run this, sorry"
        return

    test_files = 0
    tests = 0
    passed = 0

    file_list = [os.path.join(EXTENSIONS_PATH, i)
                 for i in os.listdir(EXTENSIONS_PATH)]
    if args.filename:
        file_list = [args.filename]

    for filename in file_list:
        file_tests, file_passed = run_test_file(filename)
        if file_tests:
            tests += file_tests
            passed += file_passed
            test_files += 1

    print ("%d test files, %d unit tests, %d passed" %
           (test_files, tests, passed))


if __name__ == '__main__':
    main()

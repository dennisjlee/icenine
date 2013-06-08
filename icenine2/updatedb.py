#!/usr/bin/env python

import argparse


def main():
    parser = argparse.ArgumentParser(description='Update icenine mongo database')
    parser.add_argument('-d', '--debug',
                        help='Don''t modify database, just print messages')
    parser.add_argument('-m', '--modified_time',
                        help='Use file modification time instead of current time')
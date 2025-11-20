#!/usr/bin/env python3
import sys, argparse, json
from nnl import parse_nnl, dump_nnl

def nnl2json_text(text: str) -> str:
    data = parse_nnl(text)
    return json.dumps(data, ensure_ascii=False, indent=2)

def json2nnl_text(jtext: str) -> str:
    obj = json.loads(jtext)
    return dump_nnl(obj)

def main():
    p = argparse.ArgumentParser(prog='nnl')
    sub = p.add_subparsers(dest='cmd')
    a = sub.add_parser('nnl2json')
    a.add_argument('input', help='input file (or - for stdin)')
    b = sub.add_parser('json2nnl')
    b.add_argument('input', help='input file (or - for stdin)')
    args = p.parse_args()
    if args.cmd == 'nnl2json':
        if args.input == '-':
            txt = sys.stdin.read()
        else:
            with open(args.input, 'r', encoding='utf-8') as f: txt = f.read()
        print(nnl2json_text(txt))
    elif args.cmd == 'json2nnl':
        if args.input == '-':
            txt = sys.stdin.read()
        else:
            with open(args.input, 'r', encoding='utf-8') as f: txt = f.read()
        print(json2nnl_text(txt))
    else:
        p.print_help()

if __name__ == '__main__':
    main()

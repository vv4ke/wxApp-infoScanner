import argparse

parser = argparse.ArgumentParser(description='Description of your program')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-sp', metavar='<encrypted_file>', type=str, help='Scan encrypted file')
group.add_argument('-wf', metavar='<watch_folder>', type=str, help='Monitor folder')
group.add_argument('-sf', metavar='<scan_folder>', type=str, help='Scan folder')
parser.add_argument('--wxid', metavar='<decryption_key>', type=str, help='Decryption key for encrypted file')

args = parser.parse_args()

if args.sp:
    print(f"Scanning encrypted file: {args.sp}")
    print(f"Using decryption key: {args.wxid}")
elif args.wf:
    print(f"Monitoring folder: {args.wf}")
elif args.sf:
    print(f"Scanning folder: {args.sf}")

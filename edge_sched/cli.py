"""cli.py
Command line interface.
"""
import argparse, json, yaml, sys
from edge_sched.generator import random_dag, gen_devices, save_yaml
from edge_sched.solver_interface import solve_instance

def main():
    ap=argparse.ArgumentParser(prog='edge-sched')
    sub=ap.add_subparsers(dest='cmd')

    g=sub.add_parser('generate')
    g.add_argument('--tasks',type=int,default=50)
    g.add_argument('--devices',type=int,default=10)
    g.add_argument('-o','--output',default='instance.yaml')

    s=sub.add_parser('solve')
    s.add_argument('file')
    s.add_argument('--alpha',type=float,default=1)
    s.add_argument('--beta',type=float,default=1)
    s.add_argument('--gamma',type=float,default=1)
    s.add_argument('--timeout',type=int,default=60)

    args=ap.parse_args()
    if args.cmd=='generate':
        dag=random_dag(args.tasks)
        devs=gen_devices(args.devices)
        save_yaml(dag,devs,args.output)
        print('Generated', args.output)
    elif args.cmd=='solve':
        res=solve_instance(args.file,args.alpha,args.beta,args.gamma,args.timeout)
        print(json.dumps(res,indent=2))
    else:
        ap.print_help()

if __name__=='__main__':
    main()

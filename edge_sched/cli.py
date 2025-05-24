"""cli.py
Command line interface.
"""
import argparse, json, yaml, sys
from edge_sched.generator import layered_dag, random_dag, gen_devices, save_json
from edge_sched.solver_interface import solve_instance
from edge_sched.vis_dag import load_instance, plot_dag

def main():
    ap=argparse.ArgumentParser(prog='edge-sched')
    sub=ap.add_subparsers(dest='cmd')

    g=sub.add_parser('generate')
    g.add_argument('--tasks',type=int,default=50)
    g.add_argument('--devices',type=int,default=10)
    g.add_argument('-o','--output',default='instance.json')
    g.add_argument('--layered', action='store_true', help='Generate a layered random DAG')
    g.add_argument('--layers', type=int, default=3, help='Number of layers if using --layered')

    s=sub.add_parser('solve')
    s.add_argument('file')
    s.add_argument('--alpha',type=float,default=1)
    s.add_argument('--beta',type=float,default=1)
    s.add_argument('--gamma',type=float,default=1)
    s.add_argument('--timeout',type=int,default=60)
    s.add_argument('-o','--output',default='output.json')

    v = sub.add_parser('vis')
    v.add_argument('file', help='Input instance JSON file')
    v.add_argument('-o', '--output', help='Output image path (e.g. dag.png)', default=None)

    args=ap.parse_args()
    if args.cmd=='generate':
        if args.layered:
            dag = layered_dag(args.tasks, num_layers=args.layers)
        else:
            dag = random_dag(args.tasks)
        devs=gen_devices(args.devices)
        save_json(dag, devs, args.output)
        print('Generated', args.output)
    elif args.cmd=='solve':
        res=solve_instance(args.file,args.alpha,args.beta,args.gamma,args.timeout, args.output)
        print(json.dumps(res,indent=2))
    elif args.cmd == 'vis':
        data = load_instance(args.file)
        output_path = args.output or args.file.replace('.json', '_dag.png')
        plot_dag(data["tasks"], data["edges"], output_path)
    else:
        ap.print_help()

if __name__=='__main__':
    main()

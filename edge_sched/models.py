"""models.py
Latency and energy models.
"""
def latency_base(task_id, device, size=1):
    return device['latency_base'] + 0.01*size

def queue_delay(util, mu):
    rho = util/mu
    if rho>=1: return 1e9
    return rho/(mu - util)

def net_delay(congestion_factor):
    return congestion_factor

def total_latency(task_id, device, util, mu=1.0, cong=0.5, beta_q=1.0, beta_n=1.0):
    return latency_base(task_id, device)+beta_q*queue_delay(util,mu)+beta_n*net_delay(cong)

def piecewise_energy(util, P_idle=1.0, U1=0.3,U2=0.7,
                     s1=3.0,s2=5.0,s3=7.0):
    if util< U1:
        return P_idle + s1*util
    elif util< U2:
        return P_idle + s1*U1 + s2*(util-U1)
    else:
        return (P_idle + s1*U1 + s2*(U2-U1) +
                s3*(util-U2))

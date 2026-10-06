"""Independent circuit checks for Razavi's historical AI design experiments.

This evaluates explicit ideal models, not present-day AI accuracy or PDK results.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def close(a, b):
    np.testing.assert_allclose(a, b, rtol=1e-9, atol=1e-12)


def ring_eigenvalues(gain, taus):
    # Three individually stamped inverting first-order stages.
    state = np.diag(-1/np.asarray(taus, dtype=float))
    for k, tau in enumerate(taus):
        state[k, (k-1) % 3] = -gain/tau
    return np.linalg.eigvals(state)


def main():
    scores1 = [4,2,4,4,4,0,1,4,0,1,3,3,0,4,0,3,0,0,1,0,0,3,0,3,0,0,2,1,2,0]
    scores2 = [4,4,4,4,1,1,4,4,1,2,2,1,4,0,0,1,2,3,1,1]
    assert sum(scores1) == 49 and sum(scores2) == 44
    # Same geometry ratio and overdrive; lambda scales as inverse length.
    beta, vov, lam = .002, .2, .1
    current = beta*vov**2/2; gm = beta*vov; ro = 1/(lam*current)
    close(gm*(1/((lam/2)*current)), 2*gm*ro)
    # Diode connection derivative agrees with gm+go, not a high-Z current source.
    vg=.7; vt=.4; eps=1e-6
    def diode(v): return beta*(v-vt)**2*(1+lam*v)/2
    slope=(diode(vg+eps)-diode(vg-eps))/(2*eps)
    g_di = beta*(vg-vt)*(1+lam*vg)+beta*(vg-vt)**2*lam/2
    np.testing.assert_allclose(slope,g_di,rtol=1e-8)
    # PMOS stack Q19: lower gate sets X and upper device saturation headroom.
    supply,vsg1,vsg2,vt2=.95,.35,.4,.2
    vb2=supply-vsg2; overdrive2=vsg2-vt2
    lower_gate_limit=vb2+vt2-vsg1
    close(lower_gate_limit,supply-overdrive2-vsg1)
    example_gate=.5; node_x=example_gate+vsg1
    assert example_gate<overdrive2+vsg1  # Printed source bound would allow this.
    assert supply-node_x<overdrive2    # Actual upper-device saturation fails.
    # Figure 16: lower PMOS follower, upper NMOS common-gate; no body effect.
    g1,g2,go2=.002,.004,.0001
    vx,vo=np.linalg.solve([[g1+g2+go2,-go2],[-g2-go2,go2]],[0,1])
    follower_cg_ro=1/go2+(1+g2/go2)/g1
    close(vo,follower_cg_ro)
    # Source follower with gate resistor and Cgs: explicit gate/output KCL.
    rg,cgs=5000.,100e-15; gms=.002
    for f in np.geomspace(1e3,1e11,61):
        s=2j*np.pi*f
        vg,vo=np.linalg.solve([[1/rg+s*cgs,-s*cgs],[-gms-s*cgs,gms+s*cgs]],[0,1])
        close(vo,(1+s*rg*cgs)/(gms+s*cgs))
    # Figure 22 positive loop: a negative conductance determinant yields RHP mode.
    state_positive=-np.array([[.0001,.002],[.002,.0001]])/100e-15
    assert max(np.linalg.eigvals(state_positive))>0
    # Generalized two-node capacitor matrix has rank 2 with independent shunts.
    cmat=np.array([[30,-10],[-10,40]],dtype=float)*1e-15
    assert np.linalg.matrix_rank(cmat)==2
    assert np.all(np.linalg.eigvalsh(cmat)>0)
    # Uniform ring time scaling versus one dominant pole; compare state eigenvalues
    # with the independently multiplied transfer-function polynomial.
    gain=3.; tau=1e-9
    ev=ring_eigenvalues(gain,[tau]*3)
    close(np.sort_complex(ev*2),np.sort_complex(ring_eigenvalues(gain,[tau/2]*3)))
    ratios=np.geomspace(1,100,401); maxreal=[]
    for ratio in ratios:
        roots=np.roots([ratio,1+2*ratio,2+ratio,1+gain**3])
        state_roots=ring_eigenvalues(gain,[ratio*tau,tau,tau])*tau
        np.testing.assert_allclose(np.sort_complex(roots),np.sort_complex(state_roots),rtol=1e-8,atol=1e-10)
        maxreal.append(max(roots.real))
    upper_ratio=((gain**3-4)+np.sqrt((gain**3-4)**2-16))/4
    assert max(ring_eigenvalues(gain,[tau]*3).real)>0
    assert max(ring_eigenvalues(gain,[100*tau,tau,tau]).real)<0
    # Dynamic supply average resistance and actual incremental resistance.
    n,cnode,fs,vs,kf=3,100e-15,1e9,.8,1e9
    def current_supply(v):return n*cnode*(fs+kf*(v-vs))*v
    average_r=vs/current_supply(vs)
    increment_r=1/(n*cnode*(fs+vs*kf))
    close(1/((current_supply(vs+eps)-current_supply(vs-eps))/(2*eps)),increment_r)
    # Initial integrating gain: fixed duration versus capacitor-set threshold time.
    c0,ic,gin,vth=100e-15,100e-6,.001,.4
    cs=c0*np.linspace(.5,4,200)
    tend=cs*vth/ic
    endpoint_gain=gin*tend/cs
    close(endpoint_gain,gin*vth/ic)
    # Clocked path series resistance versus increasing capacitive load.
    rdata,rclock,cap0,capw=1000.,4000.,20e-15,5e-15
    wopt=np.sqrt(rclock*cap0/(rdata*capw))
    def delay(w): return (rdata+rclock/w)*(cap0+capw*w)
    assert delay(wopt)<delay(1) and delay(wopt)<delay(20)
    # Finite output resistance feedback input impedance versus two-node KCL.
    a0,rf,rout=10.,2000.,500.
    vin,vout=np.linalg.solve([[1/rf,-1/rf],[a0/rout-1/rf,1/rout+1/rf]],[1,0])
    close(vin,(rf+rout)/(1+a0))
    loaded_gain=a0*rf/(rf+rout)
    naive_r=rf/(1+loaded_gain)
    # One-sided white supply PSD, Hz/V pushing, and SSB conversion.
    pushing,sv,offset=1e9,1e-16,1e6
    ssb=pushing**2*sv/(2*offset**2)
    # Weak quadrature coupling from parallel tank phase, exact positive branch.
    alpha,q=.2,10.
    x=(alpha/q+np.sqrt((alpha/q)**2+4))/2
    close(q*(x-1/x),alpha)
    shifts=[];qs=np.linspace(5,40,200)
    for quality in qs:
        exact=(alpha/quality+np.sqrt((alpha/quality)**2+4))/2-1
        approx=alpha/(2*quality)
        assert abs(exact-approx)/approx<.011
        shifts.append(exact)
    figs=ROOT/'figures';figs.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.3})
    fig,axes=plt.subplots(2,2,figsize=(11,8))
    axes[0,0].semilogx(ratios,maxreal)
    axes[0,0].axhline(0,color='gray',ls=':')
    axes[0,0].axvline(upper_ratio,color='tab:red',ls='--',label=f'Upper stability boundary {upper_ratio:.2f}')
    axes[0,0].set(xlabel='One node time constant / other nodes',ylabel='Maximum real pole × base tau',title='Three-stage linear ring, stage gain=3')
    axes[0,0].legend(fontsize=8)
    axes[0,1].plot(cs/c0,endpoint_gain,label='Threshold endpoint')
    axes[0,1].plot(cs/c0,gin*(c0*vth/ic)/cs,label='Fixed observation time')
    axes[0,1].set(xlabel='Integrating capacitance / baseline',ylabel='Initial gain magnitude',title='The observation rule changes the trend')
    axes[0,1].legend()
    ws=np.linspace(.5,20,201)
    axes[1,0].plot(ws,delay(ws)/1e-12)
    axes[1,0].axvline(wopt,color='tab:red',ls='--',label=f'Model optimum W={wopt:.2f}')
    axes[1,0].set(xlabel='Clocked-device width scale',ylabel='RC delay estimate (ps)',title='Drive improves while loading grows')
    axes[1,0].legend(fontsize=8)
    axes[1,1].plot(qs,100*np.array(shifts),label='Exact tank phase model')
    axes[1,1].plot(qs,100*alpha/(2*qs),ls='--',label='Weak-detuning approximation')
    axes[1,1].set(xlabel='Parallel tank Q',ylabel='Positive frequency shift (%)',title='Fixed injection ratio alpha=0.2')
    axes[1,1].legend(fontsize=8)
    fig.tight_layout();fig.savefig(figs/'ai_circuit_review_models.png',dpi=180);plt.close(fig)
    print(json.dumps({'source_A1_points':sum(scores1),'source_A1_percent':sum(scores1)/120*100,
                     'source_A2_points':sum(scores2),'source_A2_percent':sum(scores2)/80*100,
                     'follower_plus_CG_Rout_ohm':follower_cg_ro,
                     'PMOS_lower_gate_upper_bound_V':lower_gate_limit,
                     'single_loaded_ring_upper_tau_ratio':upper_ratio,
                     'supply_average_R_ohm':average_r,'supply_incremental_R_ohm':increment_r,
                     'initial_threshold_endpoint_gain':float(endpoint_gain[0]),
                     'clocked_path_width_optimum':wopt,
                     'finite_Rout_feedback_Rin_ohm':float(vin),'naive_loaded_gain_Rin_ohm':naive_r,
                     'supply_SSB_dBc_per_Hz':10*np.log10(ssb),
                     'quadrature_exact_shift_percent':(x-1)*100,
                     'quadrature_approx_shift_percent':alpha/(2*q)*100},indent=2))
    print('Independent KCL, state/polynomial, charge-timing, parameter-trend and score checks passed.')


if __name__=='__main__':main()

from numba.typed import List
#import multivelo as mv
import numpy as np

def predict_exp(tau,
                c0,
                u0,
                s0,
                alpha_c,
                alpha,
                beta,
                gamma,
                scale_cc=1,
                pred_r=True,
                chrom_open=True,
                backward=False,
                rna_only=False,
                style='multivelo'):

    if len(tau) == 0:
        return np.empty((0, 3))
    if backward:
        tau = -tau
    res = np.empty((len(tau), 3))
    if style == 'multivelo':
        
        eat = np.exp(-alpha_c * tau)
        ebt = np.exp(-beta * tau)
        egt = np.exp(-gamma * tau)
        if rna_only:
            kc = 1
            c0 = 1
        else:
            if chrom_open:
                kc = 1
            else:
                kc = 0
                alpha_c *= scale_cc

        const = (kc - c0) * alpha / (beta - alpha_c)

        res[:, 0] = kc - (kc - c0) * eat

        if pred_r:

            res[:, 1] = u0 * ebt + (alpha * kc / beta) * (1 - ebt)
            res[:, 1] += const * (ebt - eat)

            res[:, 2] = s0 * egt + (alpha * kc / gamma) * (1 - egt)
            res[:, 2] += ((beta / (gamma - beta)) *
                        ((alpha * kc / beta) - u0 - const) * (egt - ebt))
            res[:, 2] += (beta / (gamma - alpha_c)) * const * (egt - eat)

        else:
            res[:, 1] = np.zeros(len(tau))
            res[:, 2] = np.zeros(len(tau))
        return res

    elif style == 'moflow':
        if rna_only:
            kc = 1
            c0 = 1
        else:
            if chrom_open:
                kc = 1
            else:
                kc = -1
                alpha_c *= scale_cc
                
        eat = np.exp(kc * alpha_c * tau)
        ebt = np.exp(-beta * tau)
        egt = np.exp(-gamma * tau)
        

        const = alpha*c0 / (kc*alpha_c + beta)

        res[:, 0] = c0*eat

        if pred_r:

            res[:, 1] = (u0 - const)*ebt + const * eat

            res[:, 2] = alpha*const*eat/(gamma-kc*alpha_c)
            res[:, 2] += beta(u0 - const)*ebt/(gamma + beta)
            res[:, 2] += (s0 - beta*const/(gamma-kc*alpha_c) - beta*(u0 - const)/(gamma+beta))*egt
            

        else:
            res[:, 1] = np.zeros(len(tau))
            res[:, 2] = np.zeros(len(tau))
        return res
        

def generate_exp(tau_list,
                 t_sw_array,
                 alpha_c,
                 alpha,
                 beta,
                 gamma,
                 scale_cc=1,
                 model=1,
                 rna_only=False,
                 style='multivelo'):

    if beta == alpha_c:
        beta += 1e-3
    if gamma == beta or gamma == alpha_c:
        gamma += 1e-3
    switch = len(t_sw_array)
    if switch >= 1:
        tau_sw1 = np.array([t_sw_array[0]])
        if switch >= 2:
            tau_sw2 = np.array([t_sw_array[1] - t_sw_array[0]])
            if switch == 3:
                tau_sw3 = np.array([t_sw_array[2] - t_sw_array[1]])
    exp_sw1, exp_sw2, exp_sw3 = (np.empty((0, 3)),
                                 np.empty((0, 3)),
                                 np.empty((0, 3)))
    tau1 = tau_list[0]
    if switch >= 1:
        tau2 = tau_list[1]
        if switch >= 2:
            tau3 = tau_list[2]
            if switch == 3:
                tau4 = tau_list[3]
    exp1, exp2, exp3, exp4 = (np.empty((0, 3)), np.empty((0, 3)),
                              np.empty((0, 3)), np.empty((0, 3)))
    if model == 0:
        exp1 = predict_exp(tau1, 0, 0, 0, alpha_c, alpha, beta, gamma,
                           pred_r=False, scale_cc=scale_cc, rna_only=rna_only, style=style)
        if switch >= 1:
            exp_sw1 = predict_exp(tau_sw1, 0, 0, 0, alpha_c, alpha, beta,
                                  gamma, pred_r=False, scale_cc=scale_cc,
                                  rna_only=rna_only, style=style)
            exp2 = predict_exp(tau2, exp_sw1[0, 0], exp_sw1[0, 1],
                               exp_sw1[0, 2], alpha_c, alpha, beta, gamma,
                               pred_r=False, chrom_open=False,
                               scale_cc=scale_cc, rna_only=rna_only, style=style)
            if switch >= 2:
                exp_sw2 = predict_exp(tau_sw2, exp_sw1[0, 0], exp_sw1[0, 1],
                                      exp_sw1[0, 2], alpha_c, alpha, beta,
                                      gamma, pred_r=False, chrom_open=False,
                                      scale_cc=scale_cc, rna_only=rna_only, style=style)
                exp3 = predict_exp(tau3, exp_sw2[0, 0], exp_sw2[0, 1],
                                   exp_sw2[0, 2], alpha_c, alpha, beta, gamma,
                                   chrom_open=False, scale_cc=scale_cc,
                                   rna_only=rna_only, style=style)
                if switch == 3:
                    exp_sw3 = predict_exp(tau_sw3, exp_sw2[0, 0],
                                          exp_sw2[0, 1], exp_sw2[0, 2],
                                          alpha_c, alpha, beta, gamma,
                                          chrom_open=False, scale_cc=scale_cc,
                                          rna_only=rna_only, style=style)
                    exp4 = predict_exp(tau4, exp_sw3[0, 0], exp_sw3[0, 1],
                                       exp_sw3[0, 2], alpha_c, 0, beta, gamma,
                                       chrom_open=False, scale_cc=scale_cc,
                                       rna_only=rna_only, style=style)
    elif model == 1:
        exp1 = predict_exp(tau1, 0, 0, 0, alpha_c, alpha, beta, gamma,
                           pred_r=False, scale_cc=scale_cc, rna_only=rna_only, style=style)
        if switch >= 1:
            exp_sw1 = predict_exp(tau_sw1, 0, 0, 0, alpha_c, alpha, beta,
                                  gamma, pred_r=False, scale_cc=scale_cc,
                                  rna_only=rna_only, style=style)
            exp2 = predict_exp(tau2, exp_sw1[0, 0], exp_sw1[0, 1],
                               exp_sw1[0, 2], alpha_c, alpha, beta, gamma,
                               scale_cc=scale_cc, rna_only=rna_only, style=style)
            if switch >= 2:
                exp_sw2 = predict_exp(tau_sw2, exp_sw1[0, 0], exp_sw1[0, 1],
                                      exp_sw1[0, 2], alpha_c, alpha, beta,
                                      gamma, scale_cc=scale_cc,
                                      rna_only=rna_only, style=style)
                exp3 = predict_exp(tau3, exp_sw2[0, 0], exp_sw2[0, 1],
                                   exp_sw2[0, 2], alpha_c, alpha, beta, gamma,
                                   chrom_open=False, scale_cc=scale_cc,
                                   rna_only=rna_only, style=style)
                if switch == 3:
                    exp_sw3 = predict_exp(tau_sw3, exp_sw2[0, 0],
                                          exp_sw2[0, 1], exp_sw2[0, 2],
                                          alpha_c, alpha, beta, gamma,
                                          chrom_open=False, scale_cc=scale_cc,
                                          rna_only=rna_only, style=style)
                    exp4 = predict_exp(tau4, exp_sw3[0, 0], exp_sw3[0, 1],
                                       exp_sw3[0, 2], alpha_c, 0, beta, gamma,
                                       chrom_open=False, scale_cc=scale_cc,
                                       rna_only=rna_only, style=style)
    elif model == 2:
        exp1 = predict_exp(tau1, 0, 0, 0, alpha_c, alpha, beta, gamma,
                           pred_r=False, scale_cc=scale_cc, rna_only=rna_only, style=style)
        if switch >= 1:
            exp_sw1 = predict_exp(tau_sw1, 0, 0, 0, alpha_c, alpha, beta,
                                  gamma, pred_r=False, scale_cc=scale_cc,
                                  rna_only=rna_only, style=style)
            exp2 = predict_exp(tau2, exp_sw1[0, 0], exp_sw1[0, 1],
                               exp_sw1[0, 2], alpha_c, alpha, beta, gamma,
                               scale_cc=scale_cc, rna_only=rna_only, style=style)
            if switch >= 2:
                exp_sw2 = predict_exp(tau_sw2, exp_sw1[0, 0], exp_sw1[0, 1],
                                      exp_sw1[0, 2], alpha_c, alpha, beta,
                                      gamma, scale_cc=scale_cc,
                                      rna_only=rna_only, style=style)
                exp3 = predict_exp(tau3, exp_sw2[0, 0], exp_sw2[0, 1],
                                   exp_sw2[0, 2], alpha_c, 0, beta, gamma,
                                   scale_cc=scale_cc, rna_only=rna_only, style=style)
                if switch == 3:
                    exp_sw3 = predict_exp(tau_sw3, exp_sw2[0, 0],
                                          exp_sw2[0, 1], exp_sw2[0, 2],
                                          alpha_c, 0, beta, gamma,
                                          scale_cc=scale_cc, rna_only=rna_only, style=style)
                    exp4 = predict_exp(tau4, exp_sw3[0, 0], exp_sw3[0, 1],
                                       exp_sw3[0, 2], alpha_c, 0, beta, gamma,
                                       chrom_open=False, scale_cc=scale_cc,
                                       rna_only=rna_only, style=style)
    return (exp1, exp2, exp3, exp4), (exp_sw1, exp_sw2, exp_sw3)


def simulate(n_cell, param, t_sw_array, total_h=20, direction='complete',
            model=1, style='multivelo'):
    
    t = np.linspace(0, total_h, n_cell)

    param = np.clip(param, 1e-3, None)
    if len(param.shape) == 1:
        
        alpha_c, alpha, beta, gamma = param
        if beta == alpha_c:
            beta += 1e-3
        if gamma == beta or gamma == alpha_c:
            gamma += 1e-3
    else:
        alpha_c, alpha, beta, gamma = [param[:, i] for i in range(4)]    
    if direction=='complete':
        state0 = t <= t_sw_array[0]
        state1 = (t_sw_array[0] < t) & (t <= t_sw_array[1])
        state2 = (t_sw_array[1] < t) & (t <= t_sw_array[2])
        state3 = t_sw_array[2] < t

        tau1 = t[state0]
        tau2 = t[state1] - t_sw_array[0]
        tau3 = t[state2] - t_sw_array[1]
        tau4 = t[state3] - t_sw_array[2]
        tau_list = [tau1, tau2, tau3, tau4]
        switch = np.sum(t_sw_array < total_h)
        typed_tau_list = List()
        [typed_tau_list.append(x) for x in tau_list]

        exp_list, exp_sw_list = generate_exp(typed_tau_list,
                        t_sw_array[:switch],
                        alpha_c,
                        alpha,
                        beta,
                        gamma,
                        scale_cc=1,
                        model=model,
                        rna_only=False,
                        style=style)
        c = np.empty(len(t))
        u = np.empty(len(t))
        s = np.empty(len(t))
        for i, ii in enumerate([state0, state1, state2, state3]):
            if np.any(ii):
                c[ii] = exp_list[i][:, 0]
                u[ii] = exp_list[i][:, 1]
                s[ii] = exp_list[i][:, 2]
    elif direction=='on':
        state0 = t <= t_sw_array[0]
        state1 = t > t_sw_array[0]
        tau1 = t[state0]
        tau2 = t[state1] - t_sw_array[0]
        tau_sw1 = np.array([t_sw_array[0]])
        
        exp_sw1 = np.empty((0, 3))
        exp_sw1 = mv.dynamical_chrom_func.predict_exp(tau_sw1, 0, 0, 0, alpha_c, alpha, beta,
                                    gamma, pred_r=False)
        exp1 = mv.dynamical_chrom_func.predict_exp(tau1, 0, 0, 0, alpha_c, alpha, beta, gamma,
                        pred_r=False)
        exp2 = mv.dynamical_chrom_func.predict_exp(tau2, exp_sw1[0, 0], exp_sw1[0, 1],
                            exp_sw1[0, 2], alpha_c, alpha, beta, gamma,
        )
        exp_list = [exp1, exp2]
        c = np.empty(len(t))
        u = np.empty(len(t))
        s = np.empty(len(t))
        for i, ii in enumerate([state0, state1]):
            if np.any(ii):
                c[ii] = exp_list[i][:, 0]
                u[ii] = exp_list[i][:, 1]
                s[ii] = exp_list[i][:, 2]
        
    else:
        state0 = t <= t_sw_array[0]
        state1 = t > t_sw_array[0]
        tau1 = t[state0]
        tau2 = t[state1] - t_sw_array[0]
        tau_sw1 = np.array([t_sw_array[0]])
        
        exp_sw1 = np.empty((0, 3))
        if model==1:
            exp_sw1 = mv.dynamical_chrom_func.predict_exp(tau_sw1, 1, 1, 1, alpha_c, alpha, beta,
                                    gamma, chrom_open=False)
            exp1 = mv.dynamical_chrom_func.predict_exp(tau1,  1, 1, 1, alpha_c, alpha, beta, gamma,
                        chrom_open=False)
            exp2 = mv.dynamical_chrom_func.predict_exp(tau2, exp_sw1[0, 0], exp_sw1[0, 1],
                            exp_sw1[0, 2], alpha_c, 0, beta, gamma,
                            chrom_open=False,
            )
            exp_list = [exp1, exp2]
        elif model==2:
            exp_sw1 = mv.dynamical_chrom_func.predict_exp(tau_sw1, 1, 1, 1, alpha_c, 0, beta,
                                    gamma)
            exp1 = mv.dynamical_chrom_func.predict_exp(tau1,  1, 1, 1,  alpha_c, 0, beta, gamma,
                        )
            exp2 = mv.dynamical_chrom_func.predict_exp(tau2, exp_sw1[0, 0], exp_sw1[0, 1],
                            exp_sw1[0, 2], alpha_c, 0, beta, gamma,
                            chrom_open=False, 
            )
            exp_list = [exp1, exp2]
            
        c = np.empty(len(t))
        u = np.empty(len(t))
        s = np.empty(len(t))
        for i, ii in enumerate([state0, state1]):
            if np.any(ii):
                c[ii] = exp_list[i][:, 0]
                u[ii] = exp_list[i][:, 1]
                s[ii] = exp_list[i][:, 2]


    
    return c, u, s

    
    
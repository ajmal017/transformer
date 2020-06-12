from scipy.optimize import minimize
import numpy as np

def jumpWingsVol( ns, sigma0, a, b, c, p ) :
    var = sigma0*sigma0*( 1 + a * np.log( b * np.exp(c * ns ) + (1-b) * np.exp(-p*ns)))
    return np.sqrt(var)

def fit_chi2( nss, ys, ebs, arg):
    sigma0 = arg[0]
    a = arg[1]
    b = arg[2]
    c = arg[3]
    p = arg[4]
    
    y_fit = jumpWingsVol( nss, sigma0, a, b, c, p )
    return sum((y_fit - ys) * (y_fit - ys) /(ebs * ebs))


def func_maker( nss, ys, ebs ):
    def my_func(x) :
        return fit_chi2( nss, ys, ebs, x)
    return my_func

def callback(xk):
    print(xk)

def volFitter( nss, ys, ebs, vol_guess = [0.3, 0.5, 0.3, 1,1 ] ) :
    res = minimize( func_maker(nss, ys, ebs ), vol_guess, bounds=[[0,1],[0,1],[0.01,1],[0.1,9],[0.1,9]],
                  options={'disp':True})
    return res
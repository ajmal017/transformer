from scipy.optimize import minimize
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C


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


def volFitterGPR( nss, y, dy ) :
    X = [ [xx] for xx in nss]

    kernel = kernel = C(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2))

    gp = GaussianProcessRegressor(kernel=kernel, alpha=dy ** 2,
                              n_restarts_optimizer=10)

    # Fit to data using Maximum Likelihood Estimation of the parameters
    gp.fit(X, y)

    # Make the prediction on the meshed x-axis (ask for MSE as well)
    y_pred, sigma = gp.predict(X, return_std=True)
    return ( y_pred, sigma )


def GP_volfit_util_maker( xs, ys, es ) :
    def my_func( x_vec ) :
        obs_var=np.diag(es*es)
        K11=np.matrix(obs_var)+np.matrix([[ x_vec[0]**2*np.exp(-(x1-x2)**2 / (2*x_vec[1]**2)) for x1 in xs ] for x2 in xs ] )
        util_val=np.log(np.linalg.det(K11)) + np.dot(np.dot( np.linalg.inv(K11),ys),np.matrix(ys).transpose())
        return util_val[0,0]
    return my_func


def optimizeGPTransformer( xs, ys, es, x_guess, bounds = [[0.001,1],[0.1,10]] ) :
    res = minimize( GP_volfit_util_maker( xs,ys,es), x_guess, bounds=bounds,
                  options={'disp':True})
    return res


def fitGPTransformer( xs, ys, es, x_guess, bounds = [[0.001,1],[0.1,10]] ) :
    fit_res = optimizeGPTransformer( xs, ys, es, x_guess, bounds )
    if fit_res.success == True :
        sigma0= fit_res.x[0]
        length_scale = fit_res.x[1]
        K11_new = np.matrix( [[ sigma0**2*np.exp( -(x1-x2)**2 / (2*length_scale**2) ) for x1 in xs ] for x2 in xs ] )
        K22 = K11_new
        K12 = K11_new
        obs_var = np.diag(es * es )
        K11= np.matrix(obs_var) + K11_new
        out = np.dot( K12, np.dot( np.linalg.inv(K11) , ys ).transpose() )
        return np.array( out ).flatten()
    else :
        print( 'fit failed: ', str( fit_res ) ) 
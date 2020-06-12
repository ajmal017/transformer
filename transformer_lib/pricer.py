# transformer library on european pricer
# Rongrong Zhao April 2020

from scipy.stats import norm
import numpy as np
import math
from scipy.optimize import root

def callPrice( s, x, r, sigma, t):
    a = (np.log(s/x) + t * (r + sigma * sigma/2.0) ) / \
        (np.sqrt(t) * sigma )
    b = a - np.sqrt(t) * sigma
    return s * norm.cdf(a) - np.exp(-r * t) * norm.cdf(b) * x
    
def putPrice(s, x, r, sigma, t):
    callPrc = callPrice(s, x, r, sigma, t)
    return callPrc - s + x * np.exp(-r * t)

def optionD1( s, x, r, sigma, t ) :
    return (np.log(s/x) + t * (r + sigma * sigma/2.0)) / (np.sqrt(t) * sigma )

def optionD2( s, x, r, sigma, t ) :
    return optionD1( s, x, r, sigma, t ) - sigma * np.sqrt(t)

def optionZPlus( s, x, r, sigma, t ):
    return np.log(x/s) - t*r + t*sigma*sigma/2.0

def optionZMinus( s, x, r, sigma, t ):
    return np.log(x/s)- t*r - t*sigma*sigma/2.0

def optionZZPlus( s, x, r, sigma, t ):
    return (np.log(x/s) + t*r + t*sigma*sigma/2.0)/(np.sqrt(t) * sigma )

def optionZZMinus( s, x, r, sigma, t ):
    return (np.log(x/s) + t*r - t*sigma*sigma/2.0)/(np.sqrt(t) * sigma )

def optionDelta(s, x, r, sigma, t, optType='Call') :
    d1 = optionD1(s, x, r, sigma, t)
    if optType == 'Call' or optType =='C':
        return norm.cdf(d1)
    elif optType =='Put' or optType =='P' :
        return norm.cdf(d1) - 1
    else :
        print( 'optType has to be Call/Put, or C/P, return' )
        return 

def optionVega(s, x, r, sigma, t, optType='Call') :
    d1 = optionD1(s, x, r, sigma, t)
    return s * norm.pdf(d1)*np.sqrt(t)
    
def optionTheta( s, x, r, sigma, t, optType='Call' ) :
    d1 = optionD1( s, x, r, sigma, t )
    d2 = optionD2( s, x, r, sigma, t )
    vega = s * norm.pdf(d1)*np.sqrt(t)
    if optType == 'Call' or optType =='C':
        return vega * sigma / ( 2 * t) + r*x*norm.cdf(d2)*np.exp(-r*t)
    elif optType =='Put' or optType =='P' :
        return vega * sigma / ( 2 * t) - r*x*(1-norm.cdf(d2))*np.exp(-r*t)

def optionGamma( s, x, r, sigma, t, optType='Call' ) :
    d1 = optionD1(s, x, r, sigma, t)
    return norm.pdf(d1)/(s*sigma*np.sqrt(t))

def optionVanna( s, x, r, sigma, t, optType='Call' ) :
    return optionGamma( s, x, r, sigma, t )*s*optionZPlus( s, x, r, sigma, t )/sigma

def optionVolga( s, x, r, sigma, t, optType='Call' ) :
    return optionGamma(s,x,r,sigma,t)*s*s*optionZPlus(s,x,r,sigma,t)*optionZMinus(s,x,r,sigma,t)/(sigma*sigma)

def optionThetaTheta( s, x, r, sigma, t, optType='Call' ) :
    d2 = optionD2(s, x, r, sigma, t)
    term1 = (-1)*optionVega(s, x, r, sigma, t, optType)*sigma/(4*t*t)
    term2 = s*sigma/(2*np.sqrt(t))*dNprimed1dtau( s, x, r, sigma, t )
    term3 = (-1)*r*r*x*norm.cdf(d2)*np.exp(-r*t)
    term4 = r*x*np.exp(-r*t)*norm.pdf(d2)*optionZZMinus(s, x, r, sigma, t)/(2*t)
    return term1+term2+term3+term4

def optionThetaTheta_SM( s, x, r, sigma, t, optType='Call' ) :
    theta_cur = optionTheta(s, x, r, sigma, t, optType )
    theta_fut = optionTheta(s, x, r, sigma, t - 0.0001, optType )
    return (theta_fut - theta_cur)/(-0.0001)
    
def optionDeltaTheta( s, x, r, sigma, t, optType='Call' ) :
    d1 = optionD1(s, x, r, sigma, t)
    return norm.pdf(d1)*optionZZPlus(s, x, r, sigma, t)/(2*t)

def optionDeltaTheta_SM( s, x, r, sigma, t, optType='Call' ) :
    delta_cur = optionDelta(s, x, r, sigma, t, optType)
    delta_fut = optionDelta(s, x, r, sigma, t - 0.0001, optType)
    return (delta_fut - delta_cur )/(-0.0001)
    
def optionVegaTheta( s, x, r, sigma, t, optType='Call' ):    
    vega = optionVega( s, x, r, sigma, t, optType )
    return vega/(2*t) + s*np.sqrt(t)*dNprimed1dtau( s, x, r, sigma, t )

def optionVegaTheta_SM( s, x, r, sigma, t, optType='Call' ) :
    vega_cur = optionVega(s, x, r, sigma, t, optType)
    vega_fut = optionVega(s, x, r, sigma, t - 0.0001, optType)
    return (vega_fut - vega_cur )/(-0.0001)

def optionGammaDelta( s, x, r, sigma, t, optType='Call' ) :
    d1 = optionD1(s, x, r, sigma, t)
    gamma = optionGamma(s, x, r, sigma, t, optType)
    return -gamma/s - gamma*d1/(s*sigma*np.sqrt(t))
    
def optionGammaDelta_SM( s, x, r, sigma, t, optType='Call' ) :
    gamma_ps = optionGamma( s + s*0.001, x, r, sigma, t, optType )
    gamma_ms = optionGamma( s - s*0.001, x, r, sigma, t, optType )
    return (gamma_ps - gamma_ms ) / ( 0.002 * s )

def optionGammaTheta( s, x, r, sigma, t, optType='Call' ) :
    gamma = optionGamma(s, x, r, sigma, t, optType)
    d1 = optionD1(s,x,r,sigma,t)
    return -gamma/(2*t) - gamma*d1*optionZZPlus(s, x, r, sigma, t)/(2*t)

def optionGammaTheta_SM( s, x, r, sigma, t, optType='Call' ) :
    gamma_cur = optionGamma( s, x, r, sigma, t, optType )
    gamma_fut = optionGamma( s, x, r, sigma, t - 0.0001, optType )
    return ( gamma_fut - gamma_cur ) / (-0.0001)

def optionGammaVega( s, x, r, sigma, t, optType='Call' ) :
    zplus = optionZPlus(s, x, r, sigma, t)
    zminus = optionZMinus(s, x, r, sigma, t)
    gamma = optionGamma( s, x, r, sigma, t, optType )
    return gamma*zplus*zminus/(sigma*sigma*sigma*t) - gamma/sigma

def dNprimed1dtau( s, x, r, sigma, t ):
    d1 = optionD1( s, x, r, sigma, t )
    Nprimed1 = norm.pdf( d1 )
    return Nprimed1 * (-1)*d1*optionZZPlus( s, x, r, sigma, t )/(2*t)
    
def optionVannaVega( s, x, r, sigma, t, optType='Call' ) :
    zplus = optionZPlus( s, x, r, sigma, t)
    vanna = optionVanna( s, x, r, sigma, t, optType )
    gamma = optionGamma( s, x, r, sigma, t, optType )
    gammavega = optionGammaVega( s, x, r, sigma, t, optType )
    return - vanna/sigma +s*gammavega*zplus/sigma +s*gamma*t
    
def getGreeks( s, x, r, sigma, t, optType='Call' ) :    
    d1 = optionD1(s, x, r, sigma, t)
    d2 = optionD2(s, x, r, sigma, t)
    
    gamma = norm.pdf(d1)/(s*sigma*np.sqrt(t))
    vega = s * norm.pdf(d1)*np.sqrt(t)
    vanna = optionVanna( s, x, r, sigma, t, optType )
    volga = optionVolga( s, x, r, sigma, t, optType )
    theta = optionTheta( s, x, r, sigma, t, optType )
    
    if optType == 'Call' or optType =='C':
        delta = norm.cdf(d1)
#        theta = - vega * sigma / ( 2 * t) - r*x*norm.cdf(d2)*np.exp(-r*t)
        tv = callPrice( s, x, r, sigma, t )
    elif optType =='Put' or optType =='P' :
        delta = norm.cdf(d1) - 1
#        theta = - vega * sigma / ( 2 * t) + r*x*(1-norm.cdf(d2))*np.exp(-r*t)
        tv = putPrice( s, x, r, sigma, t )
    else :
        print( 'optType has to be Call/Put, or C/P, return' )
        return
    
    gammavega = optionGammaVega(s, x, r, sigma, t, optType) 
    gammadelta = optionGammaDelta(s, x, r, sigma, t, optType) 
    gammadelta_SM = optionGammaDelta_SM(s, x, r, sigma, t, optType) 
    
    gammatheta = optionGammaTheta(s, x, r, sigma, t, optType)
    gammatheta_SM = optionGammaTheta_SM(s, x, r, sigma, t, optType)
    
    vannavega = optionVannaVega( s, x, r, sigma, t, optType )
    
    deltatheta = optionDeltaTheta(s, x, r, sigma, t, optType)
    deltatheta_SM = optionDeltaTheta_SM(s, x, r, sigma, t, optType)
    
    vegatheta = optionVegaTheta(s, x, r, sigma, t, optType)
    vegatheta_SM = optionVegaTheta_SM(s, x, r, sigma, t, optType)
    
    thetatheta = optionThetaTheta(s, x, r, sigma, t, optType)
    thetatheta_SM = optionThetaTheta_SM(s, x, r, sigma, t, optType)

    #vega/t *(0.5 - d1*(2*np.log(x/s) + t * (r + sigma * sigma/2.0)) / (2*np.sqrt(t) * sigma ))
    
    return dict({'tv'   :tv, 
                 'delta':delta, 
                 'gamma':gamma, 
                 'vega' :vega, 
                 'theta':theta, 
                 'vanna':vanna, # dSdVol, further adjust delta if dSdVol correlates
                 'volga':volga, # seems very small
                 
                 'gammavega' :gammavega,  # sensitive to dS^2*dVol
                 'gammadelta':gammadelta, # sensitive to dS^3, similar to delta 
                 'gammatheta':gammatheta, # simply adjusts gamma if holding period is known
                 
                 'vannavega': vannavega,  # sensitive to dS*dVol^2, a little tough 
                 
                 'deltatheta':deltatheta, # simply adjusts delta if holding period is known
                 'vegatheta' :vegatheta,  # simply adjusts vega  if holding period is known
                 'thetatheta':thetatheta, # simply adjusts theta if holding period is known
                 
                 'gammadeltasm':gammadelta_SM,
                 'gammathetasm':gammatheta_SM,
                 'vegathetasm' :vegatheta_SM, # same as vegatheta
                 'thetathetasm':thetatheta_SM, # same as vegatheta
                 'deltathetasm':deltatheta_SM
                  })


def impVol( spot_price, strike, rate, option_price, ttx, optType = 'Call', priceEB=0, volGuess = 0.3 ):
    if optType == 'Call' or optType == 'C' :
        if option_price < spot_price - strike :
            return { 'impVol':0, 'volErrorBar' : 1e6 }
        else :
            def f(x) : return callPrice( spot_price, strike, rate, x, ttx ) - option_price
    elif optType == 'Put' or optType == 'P' :
        if option_price < strike - spot_price :
            return { 'impVol':0, 'volErrorBar' : 1e6 }
        else :
            def f(x) : return putPrice( spot_price, strike, rate, x, ttx ) - option_price

    sol = root(f, volGuess )
    if sol.success == True :
        impVol = sol.x[0]
        if priceEB != 0 :
            vega = getGreeks( spot_price, strike, rate, impVol, ttx, optType )['vega']
            return { 'impVol':impVol, 'volErrorBar': priceEB / vega }
        else:
            return { 'impVol':impVol, 'volErrorBar': 0}
    else :
        return { 'impVol':0, 'volErrorBar' : 2e6 }

    
def get_diddle_theta_pnl(s,x,r,sigma,t,t1,optType='C' ) :
    if optType=='C' :
        return callPrice(s,x,r,sigma,t1) - callPrice(s,x,r,sigma,t)
    elif optType=='P' :
        return putPrice(s,x,r,sigma,t1) - putPrice(s,x,r,sigma,t)
    
def get_diddle_vol_pnl(s,x,r,sigma,t,sigma1,optType='C' ) :
    if optType=='C' :
        return callPrice(s,x,r,sigma1,t) - callPrice(s,x,r,sigma,t)
    elif optType=='P' :
        return putPrice(s,x,r,sigma1,t) - putPrice(s,x,r,sigma,t)
    else :
        print( 'un-recoganized option type! only allow C or P')    
        
def get_diddle_spot_pnl( s,x,r,sigma,t,s1,optType='C' ) :
    if optType=='C' :
        return callPrice(s1,x,r,sigma,t) - callPrice(s,x,r,sigma,t)
    elif optType=='P' :
        return putPrice(s1,x,r,sigma,t) - putPrice(s,x,r,sigma,t)
    
# transformer library on european pricer -- class instance
# Rongrong Zhao 20 May 2020

import numpy as np
from transformer_lib import pricer
from scipy.stats import norm

class european_pricer:

    def __init__(self, spot, strike, rate, sigma, ttx, optType ):
        self.optType = optType
        self.spot = spot
        self.strike = strike
        self.rate = rate
        self.sigma = sigma
        self.ttx = ttx

    def d1(self):
        return pricer.optionD1( self.spot, self.strike, self.rate, self.sigma, self.ttx  )
    
    def d2(self):
        return pricer.optionD2( self.spot, self.strike, self.rate, self.sigma, self.ttx )
    
    def tv(self):
        if self.optType == 'Call' or self.optType =='C':
            return pricer.callPrice( self.spot, self.strike, self.rate, self.sigma, self.ttx )
        elif self.optType =='Put' or self.optType =='P' :
            return pricer.putPrice( self.spot, self.strike, self.rate, self.sigma, self.ttx )
        else:
            print( 'optType has to be C/P or Call/Put, ' + str(self.optType) + ' not allowed, return' )
            return
        
    ### basic greeks
    def delta(self):
        return pricer.optionDelta( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )
        
    def gamma(self):
        return pricer.optionGamma( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )
            
    def vega(self):
        return pricer.optionVega( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )
    
    def theta(self):
        return pricer.optionTheta( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )

    ### vanna and volga:
    def vanna(self):
        return pricer.optionVanna( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )
    
    def volga(self):
        return pricer.optionVolga( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )
    
    
    ### the rest second and third greeks:
    def deltatheta(self):
        return pricer.optionDeltaTheta( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )

    def vegatheta(self):
        return pricer.optionVegaTheta( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )
   
    def thetatheta(self):
        return pricer.optionThetaTheta( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )

    def gammadelta(self):
        return pricer.optionGammaDelta( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )

    def gammatheta(self):
        return pricer.optionGammaTheta( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )
    
    def gammavega(self):
        return pricer.optionGammaVega( self.spot, self.strike, self.rate, self.sigma, self.ttx, self.optType )
    
    
    ### return all greeks
    def greeks(self):
        return {
            'tv'   :self.tv(),
            'delta':self.delta(),
            'gamma':self.gamma(),
            'vega' :self.vega(),
            'theta':self.theta(),
            'vanna':self.vanna(),
            'volga':self.volga(),
            'gammadelta':self.gammadelta(),
            'gammatheta':self.gammatheta(),
            'gammavega' :self.gammavega(),
            'deltatheta':self.deltatheta(),
            'vegatheta' :self.vegatheta(),
            'thetatheta':self.thetatheta(),
            'd1':self.d1(),
            'd2':self.d2()
        }
    
from __future__ import annotations
import numpy as np
from hgfx.responses import (
 beta_obs,cdfgaussian_obs,gaussian_obs,gaussian_obs_offset,
 logrt_linear_binary,logrt_linear_binary_minimal,softmax,softmax_2beta,
 softmax_binary,softmax_mu3,total_log_likelihood,unitsq_sgm,unitsq_sgm_mu3)

def binary_states(n=8):
 s=np.zeros((n,3,4),dtype=np.float64); x=np.linspace(.15,.85,n)
 s[:,0,0]=x; s[:,0,1]=x*(1-x); s[:,0,2]=np.clip(x+.03,.05,.95); s[:,0,3]=.2
 s[:,1,0]=np.linspace(-.8,.8,n); s[:,1,1]=.35; s[:,1,2]=np.linspace(-.7,.9,n); s[:,1,3]=np.linspace(.2,.5,n)
 s[:,2,0]=np.linspace(-2.4,-1.4,n); s[:,2,1]=.5; s[:,2,2]=np.linspace(-2.2,-1.2,n); s[:,2,3]=.6
 return s

def categorical_states(n=8,nc=3):
 s=np.zeros((n,3,nc,4),dtype=np.float64)
 for k in range(n):
  for c in range(nc):
   s[k,0,c,0]=-.4+.25*c+.03*k; s[k,0,c,2]=-.3+.22*c+.02*k
 s[:,2,0,2]=np.linspace(-1,.2,n)
 return s

def test_p0_p1_models_keep_irregular_nan_and_total_finite():
 s=binary_states(); y=np.array([0,1,1,0,1,0,1,1.],float); u=y.copy(); irr=[3]
 cases=[
  unitsq_sgm(y,s,[np.log(12.)],irregular_trials=irr),
  unitsq_sgm_mu3(y,s,irregular_trials=irr),
  softmax_binary(y,s,[np.log(2.)],inputs=u,irregular_trials=irr),
  cdfgaussian_obs(y,s,irregular_trials=irr),
  beta_obs(np.linspace(.1,.9,8),s,[np.log(8.)],irregular_trials=irr),
  gaussian_obs(np.linspace(6.1,6.8,8),s,[np.log(.4)],irregular_trials=irr),
  gaussian_obs_offset(np.linspace(6.1,6.8,8),s,[np.log(.4),6.0],irregular_trials=irr),
  logrt_linear_binary(np.linspace(6.1,6.8,8),s,[6.2,.2,-.3,.4,-.1,np.log(.2)],inputs=u,irregular_trials=irr),
  logrt_linear_binary_minimal(np.linspace(6.1,6.8,8),s,[6.2,.2,-.3,np.log(.2)],inputs=u,irregular_trials=irr),
 ]
 for logp,yhat,res in cases:
  assert np.isnan(logp[3]) and np.isnan(yhat[3]) and np.isnan(res[3])
  assert np.isfinite(total_log_likelihood(logp))

def test_categorical_softmax_models():
 s=categorical_states(); y=np.array([1,2,3,1,3,2,1,2.]); u=np.array([1,0,1,0,1,0,1,0.])
 for logp,yhat,res in [softmax(y,s,[np.log(1.7)]),softmax_mu3(y,s)]:
  assert np.all(np.isfinite(logp)); assert np.all((yhat>0)&(yhat<1)); np.testing.assert_allclose(res,-logp)
 s5=np.zeros((8,1,3,1,2)); s5[:,0,:,0,0]=s[:,0,:,0]; s5[:,0,:,0,1]=s[:,0,:,2]
 logp,yhat,res=softmax_2beta(y,s5,[np.log(1.5),np.log(.8)],inputs=u,predorpost=2)
 assert np.all(np.isfinite(logp)); np.testing.assert_allclose(res,-logp)

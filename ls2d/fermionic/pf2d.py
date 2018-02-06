import numpy
import scipy.linalg
from latticesimulation.ls2d import contraction2d
import nnz

def initialization(n,mass2=1.0,iprt=0,auxbond=20):
   print '\n[pf2d.initialization] n=',n,' mass2=',mass2
   # Construct Z=tr(T) 
   # Shape:
   #  (2,0) (2,1) (2,2)
   #  (1,0) (1,1) (1,2)
   #  (0,0) (0,1) (0,2) . . .
   # Ordering: ludr
   zpeps = numpy.empty((n,n), dtype=numpy.object)
   # Interior
   d = 4 
   lam = 4.0+mass2
   tint = nnz.genZSite(lam,0)
   for i in range(1,n-1):
      for j in range(1,n-1):
         zpeps[i,j] = tint.copy()
   # Corners
   zpeps[0,0] = tint[:1,:,:1,:].copy()
   zpeps[0,n-1] = tint[:,:,:1,:1].copy()
   zpeps[n-1,0] = tint[:1,:1,:,:].copy()
   zpeps[n-1,n-1] = tint[:,:1,:,:1].copy()
   # Boundaries
   for j in range(1,n-1):
      zpeps[0,j] = tint[:,:,:1,:].copy()
      zpeps[j,0] = tint[:1,:,:,:].copy()
      zpeps[n-1,j] = tint[:,:1,:,:].copy()
      zpeps[j,n-1] = tint[:,:,:,:1].copy()
   # Compute scaling factor
   scale,z = contraction2d.binarySearch(zpeps,auxbond,iprt=iprt)
   # Local terms
   local2  = scale*nnz.genZSite(lam,1)
   local1a = scale*nnz.genZSite(lam,2)
   local1b = scale*nnz.genZSite(lam,3)
   zpeps = scale*zpeps
   return scale,zpeps,local2,local1a,local1b


if __name__ == '__main__':
   m = 5
   n = 2*m+1
   mass2 = 0.5
   iprt = 1
   auxbond = 30

   result = initialization(n,mass2,iprt,auxbond)
   scale,zpeps,local2,local1a,local1b = result

   # Test Z:
   from latticesimulation.ls2d import exact2d
   t2d = exact2d.genT2d(n,numpy.sqrt(mass2))
   t2d = t2d.reshape((n*n,n*n))
   tinv = scipy.linalg.inv(t2d)
   tinv = tinv.reshape((n,n,n,n))
   print '\nTest Z:'
   print 'direct detM=',scipy.linalg.det(t2d)
   print 'scale=',scale,'Z=',numpy.power(1.0/scale,n*n)

   print '\nTest local2:'
   v2a = tinv[0,0,0,0]
   v2b = tinv[0,1,0,1]
   v2c = tinv[m,m,m,m]
   print 'direct point=',(0,0),v2a 
   print 'direct point=',(0,1),v2b
   print 'direct point=',(m,m),v2c

   for auxbond in [10,20,30]:
      epeps = zpeps.copy()
      epeps[0,0] = local2[:1,:,:1,:]
      val = contraction2d.contract(epeps,auxbond)
      print 'point=',(0,0),'auxbond=',auxbond,val,val+v2a
   for auxbond in [10,20,30]:
      epeps = zpeps.copy()
      epeps[0,1] = local2[:,:,:1,:]
      val = contraction2d.contract(epeps,auxbond)
      print 'point=',(0,1),'auxbond=',auxbond,val,val+v2b
   for auxbond in [10,20,30]:
      epeps = zpeps.copy()
      epeps[m,m] = local2[:,:,:,:]
      val = contraction2d.contract(epeps,auxbond)
      print 'point=',(m,m),'auxbond=',auxbond,val,val+v2c
   
   print '\nTest local1:'
   v1a = tinv[3,3,m-1,m-2]
   v1b = tinv[m,m,m+4,m-3]
   v1c = tinv[m,m,m+3,m]
   v1d = tinv[m,m,m,m+3]
   print 'direct point=',(3,3),(m-1,m-2),v1a
   print 'direct point=',(m,m),(m+4,m-3),v1b
   print 'direct point=',(m,m),(m+3,m)  ,v1c
   print 'direct point=',(m,m),(m,m+3)  ,v1d

   print '\ncase-a:'
   for auxbond in [10,20,30]:
      epeps = zpeps.copy()
      epeps[3,3] = local1b
      epeps[m-1,m-2] = local1a
      for j in range(3):
         epeps[3,j] = numpy.einsum('ludr,d->ludr',epeps[3,j],[1,-1,-1,1])
      for j in range(m-2):
	 epeps[m-1,j] = numpy.einsum('ludr,d->ludr',epeps[m-1,j],[1,-1,-1,1])
      val = contraction2d.contract(epeps,auxbond)
      print 'point=',(3,3),(m-1,m-2),'auxbond=',auxbond,val,val+v1a
   # PATH
   for auxbond in [10,20,30]:
      epeps = zpeps.copy()
      epeps[3,3] = local1b
      epeps[m-1,m-2] = local1a
      # Changes col
      for j in range(3,m-2):
	 epeps[m-1,j] = numpy.einsum('ludr,d->ludr',epeps[m-1,j],[1,-1,-1,1])
      # Changes row
      for i in range(3,m-1):
	 epeps[i,3] = numpy.einsum('ludr,l->ludr',epeps[i,3],[1,-1,-1,1])
      val = contraction2d.contract(epeps,auxbond)
      print 'point=',(3,3),(m-1,m-2),'auxbond=',auxbond,val,val+v1a

   print '\ncase-b:'
   for auxbond in [10,20,30]:
      epeps = zpeps.copy()
      epeps[m,m] = local1b
      epeps[m+4,m-3] = local1a
      for j in range(m):
         epeps[m,j] = numpy.einsum('ludr,d->ludr',epeps[m,j],[1,-1,-1,1])
      for j in range(m-3):
	 epeps[m+4,j] = numpy.einsum('ludr,d->ludr',epeps[m+4,j],[1,-1,-1,1])
      val = contraction2d.contract(epeps,auxbond)
      print 'point=',(m,m),(m+4,m-3),'auxbond=',auxbond,val,val+v1b
   # PATH
   for auxbond in [10,20,30]:
      epeps = zpeps.copy()
      epeps[m,m] = local1b
      epeps[m+4,m-3] = local1a
      # Changes col
      for j in range(m-3,m):
	 epeps[m+4,j] = numpy.einsum('ludr,d->ludr',epeps[m+4,j],[1,-1,-1,1])
      # Changes row
      for i in range(m,m+4):
	 epeps[i,m] = numpy.einsum('ludr,l->ludr',epeps[i,m],[1,-1,-1,1])
      val = contraction2d.contract(epeps,auxbond)
      print 'point=',(m,m),(m+4,m-3),'auxbond=',auxbond,val,val+v1b

   print '\ncase-c:'
   for auxbond in [10,20,30]:
      epeps = zpeps.copy()
      epeps[m,m] = local1b
      epeps[m+3,m] = local1a
      for j in range(m):
	 epeps[m,j] = numpy.einsum('ludr,d->ludr',epeps[m,j],[1,-1,-1,1])
      for j in range(m):
	 epeps[m+3,j] = numpy.einsum('ludr,d->ludr',epeps[m+3,j],[1,-1,-1,1])
      val = contraction2d.contract(epeps,auxbond)
      print 'point=',(m,m),(m+3,m),'auxbond=',auxbond,val,val+v1c
   # PATH
   for auxbond in [10,20,30]:
      epeps = zpeps.copy()
      epeps[m,m] = local1b
      epeps[m+3,m] = local1a
      for i in range(m,m+3):
	 epeps[i,m] = numpy.einsum('ludr,l->ludr',epeps[i,m],[1,-1,-1,1])
      val = contraction2d.contract(epeps,auxbond)
      print 'point=',(m,m),(m+3,m),'auxbond=',auxbond,val,val+v1c

   print '\ncase-d:'
   for auxbond in [10,20,30]:
      epeps = zpeps.copy()
      epeps[m,m] = local1b
      epeps[m,m+3] = local1a
      for j in range(m):
	 epeps[m,j] = numpy.einsum('ludr,d->ludr',epeps[m,j],[1,-1,-1,1])
      for j in range(m+3):
	 epeps[m,j] = numpy.einsum('ludr,d->ludr',epeps[m,j],[1,-1,-1,1])
      val = contraction2d.contract(epeps,auxbond)
      print 'point=',(m,m),(m,m+3),'auxbond=',auxbond,val,val+v1d
   # PATH
   for auxbond in [10,20,30]:
      epeps = zpeps.copy()
      epeps[m,m] = local1b
      epeps[m,m+3] = local1a
      for j in range(m,m+3):
	 epeps[m,j] = numpy.einsum('ludr,d->ludr',epeps[m,j],[1,-1,-1,1])
      val = contraction2d.contract(epeps,auxbond)
      print 'point=',(m,m),(m,m+3),'auxbond=',auxbond,val,val+v1d

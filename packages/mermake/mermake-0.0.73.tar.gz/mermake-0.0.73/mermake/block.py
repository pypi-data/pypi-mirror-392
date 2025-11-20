import cupy as cp

class Block(list):
	def __init__(self, items=None):
		self.background = None
	def add(self, image):
		ifov = image.ifov
		if not self or self.ifov() == ifov:
			if self:
				del self[-1].data
			self.append(image)
			return True
		else:
			return False
	def iset(self):
		return self[0].iset
	def ifov(self):
		return self[0].ifov
	def __repr__(self):
		paths = [image.path for image in self]
		return f"Block({paths})"

	def get_XH(self,nbits=16,th_h=0,color_fl=None):
		
		drifts,all_flds,fov,fl_ref = pickle.load(open(drift_fl,'rb'))
		self.drifts,self.all_flds,self.fov,self.fl_ref = drifts,all_flds,fov,fl_ref

		XH = []
		for iH in tqdm(np.arange(len(all_flds))):
			fld = all_flds[iH]
			if tag_keep in os.path.basename(fld):
				for icol in range(ncols):
					tag = os.path.basename(fld)
					save_fl = save_folder+os.sep+fov.split('.')[0]+'--'+tag+'--col'+str(icol)+'.npz'
					Xh = np.load(save_fl,allow_pickle=True)['Xh']
					if len(Xh):
						tzxy = drifts[iH][0]
						ih = get_iH(fld) # get bit
						bit = (ih-1)*ncols+icol
						if len(Xh.shape):
							Xh = Xh[Xh[:,-1]>th_h]
							if len(Xh):

								icolR = np.array([[icol,bit]]*len(Xh))

								if color_fl is not None:
									ms = np.load(color_fl,allow_pickle=True)
									Xh[:,:3] = apply_colorcor(Xh[:,:3],ms[icol])
								Xh[:,:3]+=tzxy# drift correction
								XH_ = np.concatenate([Xh,icolR],axis=-1)
								XH.extend(XH_)
		self.XH = np.array(XH)

#!/usr/bin/python3

def salt(s):
	enc = ''
	if(s & 1):
		enc = ''
	elif(s & 0x2):
		enc = 'Twofish'
	elif(s & 0x4):
		enc = 'Blowfish'
	elif(s & 0x8):
		enc = 'DESede'
	elif(s & 0x10):
		enc = 'AES'
	elif(s & 0x20):
		enc = 'IDEA'
	pad = ''
	if(s & 0x100):
		pad = 'ECB'
	elif(s & 0x200):
		pad = 'CBC'
	elif(s & 0x1000):
		pad = 'NoPadding'
	elif(s & 0x2000):
		pad = 'PKC7Padding'
	
	print('SALT: ', hex(s))
	#s = s & 0xFFFF0000
	l2 = s & 4294901760
	
	b1 = l2 >> 16 & 0xFF
	b2 = l2 >> 24 & 0xFF

	l = (s & 17587891077120) >> 32
	
	keyl = 128
	if s & 17592186044416:
		keyl = 128
	elif s & 35184372088832:
		keyl = 256
	elif s & 70368744177664:
		keyl = 512

	return (enc, pad, keyl, (b1, b2), l)
	
if __name__ == '__main__':
	import sys
	arg = '17702237053200'
	try:
		sys.argv[1]
		arg = sys.argv[1]
	except IndexError:
		pass
	print(salt(int(arg)))


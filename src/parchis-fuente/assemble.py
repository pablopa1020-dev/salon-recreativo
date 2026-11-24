import os
H=os.path.dirname(os.path.abspath(__file__))
s=open(os.path.join(H,'game.html'),encoding='utf-8').read()
lib=open(os.path.join(H,'vendor/peerjs.min.js'),encoding='utf-8').read()
s=s.replace('/*@PEERJS@*/',lib)
open(os.path.join(H,'parchis.html'),'w',encoding='utf-8').write(s)
print('ok',len(s))

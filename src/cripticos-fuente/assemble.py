# joins game.html and clues.js into the single-file game
import os
H=os.path.dirname(os.path.abspath(__file__))
g=open(os.path.join(H,'game.html'),encoding='utf-8').read()
c=open(os.path.join(H,'clues.js'),encoding='utf-8').read().replace("if(typeof module!=='undefined')module.exports=CLUES;","")
open(os.path.join(H,'cripticos.html'),'w',encoding='utf-8').write(g.replace('/*@CLUES@*/',c))
print('ok')

"""Original procedural cooler bonfire; metres, +Y up, +Z front.

Usage: python -B build_coolerfire_model.py <basket_template.dae> <out.dae> <out_dir>
Uses the existing fire-basket template for export structure only; geometry and
textures are original. Three identical low-poly LODs, outward preview winding,
reversed DAE triangle winding for BG3, matching the accepted porta-potty pipeline.
"""
import sys, re, json, math
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import coolerfire_paint as paint

TPL, OUT, OD = sys.argv[1:4]
OD = Path(OD)
OD.mkdir(parents=True, exist_ok=True)
paint.paint(OD)
P, N, U, T = [], [], [], []


def nrm(v):
    v=np.array(v,float); length=np.linalg.norm(v)
    return v/length if length > 1e-12 else v


def face(points, name):
    normal=nrm(np.cross(np.array(points[1])-points[0], np.array(points[2])-points[0]))
    start=len(P)
    coords=[(0,0),(1,0),(1,1),(0,1)]
    for i,p in enumerate(points):
        P.append(list(p)); N.append(normal.tolist()); U.append(paint.uv(name,*coords[i]))
    for i in range(1,len(points)-1): T.append((start,start+i,start+i+1))


def box(c, half, name, rotation=None):
    c=np.array(c,float); h=np.array(half,float)
    R=np.eye(3) if rotation is None else rotation
    for axis in range(3):
        u,v=(axis+1)%3,(axis+2)%3
        for sign in (-1,1):
            pts=[]
            for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]:
                p=np.zeros(3); p[axis]=sign*h[axis];p[u]=a*h[u];p[v]=b*h[v]
                pts.append(c+R@p)
            if sign<0:pts.reverse()
            face(pts,name)


def tube(a,b,r,name,sides=8,r_end=None):
    a,b=np.array(a,float),np.array(b,float);direction=nrm(b-a)
    ref=np.array([0,1,0]) if abs(direction[1])<.9 else np.array([1,0,0])
    u=nrm(np.cross(ref,direction));v=np.cross(direction,u)
    end=r if r_end is None else r_end
    rings=[[c+(math.cos(j*2*math.pi/sides)*u+math.sin(j*2*math.pi/sides)*v)*radius
            for j in range(sides)] for c,radius in [(a,r),(b,end)]]
    for j in range(sides):
        k=(j+1)%sides
        # Face normal checked against radial midpoint to ensure outward winding.
        points=[rings[0][j],rings[0][k],rings[1][k],rings[1][j]]
        if np.dot(np.cross(points[1]-points[0],points[2]-points[0]),points[0]-a)<0:points.reverse()
        face(points,name)
    for pts,normal in [(rings[0],-direction),(rings[1],direction)]:
        for j in range(1,sides-1):
            tri=[pts[0],pts[j],pts[j+1]]
            if np.dot(np.cross(tri[1]-tri[0],tri[2]-tri[0]),normal)<0:tri.reverse()
            face(tri,name)


def rx(a):
    c,s=math.cos(a),math.sin(a)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]])


def flame(c,width,height,name,bend):
    c=np.array(c,float)
    ring=[c+np.array([width*math.cos(j*math.pi/2),0,width*.7*math.sin(j*math.pi/2)]) for j in range(4)]
    waist=[c+np.array([width*.48*math.cos(j*math.pi/2)+bend*.3,height*.5,width*.35*math.sin(j*math.pi/2)]) for j in range(4)]
    tip=c+np.array([bend,height,-width*.25])
    face(list(reversed(ring)),name)
    for j in range(4):
        k=(j+1)%4
        face([ring[j],ring[k],waist[k],waist[j]],name)
        face([waist[j],waist[k],tip],name)


# Open white styrofoam chest: a real dark cavity, heavy white rim and chips.
box((0,.11,0),(.68,.11,.43),'foam')
box((0,.22,0),(.57,.025,.33),'inside')
box((0,.40,-.385),(.68,.29,.065),'foam')
box((0,.40,.385),(.68,.29,.065),'foam')
box((-.62,.40,0),(.065,.29,.32),'foam')
box((.62,.40,0),(.065,.29,.32),'foam')
box((0,.705,.385),(.60,.025,.075),'foam')
box((0,.705,-.385),(.68,.025,.075),'foam')
box((-.62,.705,-.04),(.075,.025,.28),'foam')
box((.62,.705,-.04),(.075,.025,.28),'foam')
# Missing front corners, loose foam chunks and two charcoal-black scorched patches.
for c,h in [((-.64,.04,.55),(.08,.04,.055)),((.62,.03,.52),(.06,.03,.05))]:box(c,h,'chip')
box((-.22,.50,.453),(.13,.10,.008),'inside',rx(.12))
box((.44,.30,.453),(.11,.13,.008),'inside')
# Lid is two separated slabs: the gap is a geometric crack, not just a painted line.
lid_rotation=rx(math.radians(57))
box((-.35,1.02,-.65),(.33,.045,.43),'lid',lid_rotation)
box((.355,1.015,-.66),(.335,.045,.43),'lid',rx(math.radians(61)))
for x in [-.46,.46]:box((x,.71,-.43),(.12,.045,.045),'strap')
tube((-.5,.71,-.44),(-.5,1.18,-.87),.014,'steel',6)
# Stolen red shopping basket used as a grate: open wire bottom and low slatted sides.
for z in [-.29,.29]:box((0,.79,z),(.55,.022,.022),'red')
for x in [-.55,.55]:box((x,.79,0),(.022,.022,.29),'red')
for x in np.linspace(-.46,.46,7):box((x,.77,0),(.011,.012,.29),'red')
for z in np.linspace(-.24,.24,5):box((0,.785,z),(.55,.011,.011),'red')
for z in [-.29,.29]:
    for x in np.linspace(-.46,.46,7):box((x,.86,z),(.012,.075,.012),'red')
    box((0,.94,z),(.57,.018,.018),'red')
for x in [-.55,.55]:
    for z in [-.18,0,.18]:box((x,.86,z),(.012,.075,.012),'red')
    box((x,.94,0),(.018,.018,.30),'red')
# Coal under the grate and a faceted, solid orange/yellow/violet blaze.
for x,z in [(-.35,-.15),(-.12,.13),(.13,-.10),(.35,.14),(0,-.25)]:box((x,.69,z),(.13,.065,.10),'coal',rx(.13))
for c,w,h,col,bend in [((-.39,.78,-.12),.13,.55,'orange',-.08),
                       ((.31,.78,-.10),.17,.72,'orange',.12),
                       ((-.15,.78,.12),.16,.76,'orange',-.10),
                       ((.10,.79,.10),.14,.61,'yellow',.10),
                       ((-.32,.80,.12),.09,.39,'yellow',-.04),
                       ((.18,.79,-.12),.10,.86,'violet',-.14),
                       ((.42,.79,.10),.08,.43,'violet',.05)]:flame(c,w,h,col,bend)
# Charcoal bag: full soft-sided faceted sack, with open black mouth and loose briquettes.
box((-.98,.29,.63),(.23,.26,.17),'bag',rx(-.10))
box((-.98,.55,.64),(.19,.018,.13),'inside')
for x,z in [(-1.08,.57),(-.93,.66),(-1.02,.73)]:box((x,.58,z),(.075,.04,.05),'coal')
for x,z in [(-.68,.77),(-.80,.94),(-1.12,.90)]:box((x,.045,z),(.065,.045,.05),'coal')
# Squat yellow/red lighter-fluid tin with narrow neck and a very visible red cap.
box((.88,.25,.64),(.12,.23,.10),'fluid')
tube((.88,.48,.64),(.88,.53,.64),.045,'steel',8)
tube((.88,.53,.64),(.88,.57,.64),.055,'red',8)
# Teal rolled sleeping bag with concentric end and two dark webbing bands.
tube((-1.05,.20,-.48),(-1.05,.20,.13),.20,'teal',12)
tube((-1.05,.20,.132),(-1.05,.20,.145),.15,'strap',12)
tube((-1.05,.20,.147),(-1.05,.20,.157),.12,'teal',12)
for z in [-.36,.02]:tube((-1.05,.20,z),(-1.05,.20,z+.045),.207,'strap',12)
# Single oversized hot dog on an actual thin coat-hanger wire, safely above the grate.
wire=[(.18,1.10,.27),(.62,1.10,.27),(1.10,.72,.54),(1.35,.70,.66),
      (1.23,.55,.82),(.99,.64,.74),(1.10,.72,.54)]
for aa,bb in zip(wire,wire[1:]):tube(aa,bb,.009,'steel',5)
tube((.17,1.115,.27),(.59,1.115,.27),.059,'sausage',10)
tube((.13,1.115,.27),(.17,1.115,.27),.025,'sausage',8,r_end=.059)
tube((.59,1.115,.27),(.63,1.115,.27),.059,'sausage',8,r_end=.025)

# Export original geometry using the verified porta-potty DAE/tangent pipeline.
pos=np.array(P);nor=np.array(N);uv=np.array(U);tri=np.array(T)
pos[:,1] -= pos[:,1].min()  # Ground the lowest sleeping-bag strap at zero.
bmin,bmax=pos.min(0),pos.max(0)
print('verts',len(pos),'tris',len(tri),'min',bmin,'max',bmax)
assert len(tri)<3500
json.dump({'pos':pos.tolist(),'nor':nor.tolist(),'uv':uv.tolist(),'tri':tri.tolist()},open(OD/'coolerfire_preview.json','w'))
json.dump({'min':bmin.tolist(),'max':bmax.tolist(),'tris':len(tri)},open(OD/'coolerfire_bounds.json','w'))
dtri=tri[:,[0,2,1]]


def nz(v):
    length=np.linalg.norm(v,axis=-1,keepdims=True);length[length<1e-12]=1
    return v/length


nor=nz(nor)
p0,p1,p2=pos[dtri[:,0]],pos[dtri[:,1]],pos[dtri[:,2]]
u0,u1,u2=uv[dtri[:,0]],uv[dtri[:,1]],uv[dtri[:,2]]
e1,e2=p1-p0,p2-p0;d1,d2=u1-u0,u2-u0
den=d1[:,0]*d2[:,1]-d2[:,0]*d1[:,1];den[np.abs(den)<1e-12]=1
tang=(e1*d2[:,1:2]-e2*d1[:,1:2])/den[:,None]
CP,CN,CT,CB,CU=[],[],[],[],[]
for ti in range(len(dtri)):
    for k in range(3):
        v=dtri[ti,k];n=nor[v];t=tang[ti]-n*(n@tang[ti])
        if np.linalg.norm(t)<1e-7:
            t=np.cross(n,[0,1,0]);t=t if np.linalg.norm(t)>1e-7 else np.array([1.,0,0])
        t=t/np.linalg.norm(t)
        CP.append(pos[v]);CN.append(n);CT.append(t);CB.append(np.cross(n,t));CU.append(uv[v])
CP,CN,CT,CB,CU=[np.array(x) for x in (CP,CN,CT,CB,CU)]
key=np.round(np.concatenate([CP,CN,CT,CB,CU],1),6)
_,first,inv=np.unique(key,axis=0,return_index=True,return_inverse=True)
CP,CN,CT,CB,CU=[x[first] for x in (CP,CN,CT,CB,CU)];count=len(CP)
s=Path(TPL).read_text(encoding='utf-8-sig')
fmt=lambda a:' '.join('%.6f'%x for x in a.ravel())
pidx=' '.join('%d %d %d %d %d'%(i,i,i,i,i) for i in inv)
for name in ['LTS_GEN_Fire_Basket_A_Mesh','LTS_GEN_Fire_Basket_A_Mesh_LOD1','LTS_GEN_Fire_Basket_A_Mesh_LOD2']:
    start=s.index('<geometry id="%s-geom"'%name);end=s.index('</geometry>',start);g=s[start:end]
    for key_,arr in [('positions',CP),('normals',CN),('tangents',CT),('binormals',CB),('uvs0',CU)]:
        g,n_=re.subn(r'(<float_array id="%s-%s-array" count=")\d+(">)[^<]*(</float_array>)'%(name,key_),lambda m:m[1]+str(arr.size)+m[2]+fmt(arr)+m[3],g);assert n_==1
        g,n_=re.subn(r'(<accessor count=")\d+(" source="#%s-%s-array")'%(name,key_),lambda m:m[1]+str(count)+m[2],g);assert n_==1
    g,n_=re.subn(r'<triangles count="\d+">','<triangles count="%d">'%len(dtri),g);assert n_==1
    g,n_=re.subn(r'(<triangles[^>]*>.*?<p>)[^<]*(</p>)',lambda m:m[1]+pidx+m[2],g,flags=re.S);assert n_==1
    s=s[:start]+g+s[end:]
Path(OUT).write_text(s,encoding='utf-8')


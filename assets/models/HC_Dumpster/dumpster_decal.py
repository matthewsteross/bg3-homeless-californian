"""Original polygon parody decal, projected onto the dumpster's steel front in world space.
No source-logo pixels or paths are used. UV rasterization uses pixel-center barycentrics.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Grounded model-space rectangle: x left/right, y bottom/top (metres).
DECAL_RECT = (-0.45, 0.45, 0.34, 0.89)


def decal_image():
    """Own W and goofy five-legged M, supersampled; text is below the white plate."""
    scale = 2
    image = Image.new('RGBA', (1000*scale, 600*scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    def polygon(points, color):
        draw.polygon([(int(x*scale), int(y*scale)) for x,y in points], fill=color)
    # Right-leaning white plate; independently drawn proportions.
    polygon([(25,45),(865,45),(975,395),(135,395)], (250,250,239,255))
    polygon([(125,110),(197,110),(238,275),(279,174),(332,174),(374,275),(410,110),(484,110),
             (418,337),(350,337),(306,244),(264,337),(194,337)], (0,112,57,255))
    # Uneven stems and a deliberately absurd fifth leg underneath the tilted M valley.
    polygon([(485,337),(514,113),(585,113),(649,228),(712,133),(786,113),(850,337),
             (778,337),(744,225),(679,299),(614,217),(575,337)], (225,165,0,255))
    polygon([(643,259),(681,272),(721,376),(679,376)], (225,165,0,255))
    text='WASTE MISMANAGEMENT'
    font_path=Path('C:/Windows/Fonts/arialbd.ttf')
    font=ImageFont.truetype(str(font_path), 67*scale) if font_path.is_file() else ImageFont.load_default(size=52*scale)
    box=draw.textbbox((0,0),text,font=font,stroke_width=0)
    width=box[2]-box[0]
    if width > 950*scale and font_path.is_file():
        font=ImageFont.truetype(str(font_path),int(67*scale*950*scale/width));box=draw.textbbox((0,0),text,font=font);width=box[2]-box[0]
    draw.text(((1000*scale-width)/2,455*scale-box[1]),text,font=font,fill=(255,242,190,255),stroke_width=2*scale,stroke_fill=(10,43,25,255))
    return image.resize((1000,600),Image.Resampling.LANCZOS), str(font_path) if font_path.is_file() else 'PIL default'


def bake_decal(plain, pos, nor, uv, tri, out_dir, mirror=False):
    """Blend only projected front-panel texels; preserve the rest of the UV atlas exactly."""
    out_dir=Path(out_dir);decal,font=decal_image()
    if mirror:decal=decal.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    decal.save(out_dir/'HC_Dumpster_Decal.png')
    colors=np.asarray(plain.convert('RGB')).copy();height,width=colors.shape[:2]
    mask=np.zeros((height,width),dtype=bool);surface_mask=np.zeros_like(mask)
    art=np.asarray(decal,dtype=float);dh,dw=art.shape[:2]
    xmin,xmax,ymin,ymax=DECAL_RECT;selected=0
    for face in tri:
        p=pos[face];n=nor[face]
        # Geometric face normal is more stable than just one vertex normal at panel seams.
        geom=np.cross(p[1]-p[0],p[2]-p[0]);length=np.linalg.norm(geom)
        if length<1e-12:continue
        if geom @ n.mean(0)<0:geom=-geom
        if geom[2]/length<=0.7 or n[:,2].mean()<=0.7:continue
        if p[:,2].max()<0.30 or p[:,1].min()>ymax or p[:,1].max()<ymin or p[:,0].min()>xmax or p[:,0].max()<xmin:continue
        coords=uv[face]*[width,-height]+[0,height]
        lo=np.maximum(np.floor(coords.min(0)).astype(int),0);hi=np.minimum(np.ceil(coords.max(0)).astype(int),[width-1,height-1])
        if np.any(hi<lo):continue
        xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1));points=np.stack([xx+0.5,yy+0.5],axis=-1)
        a,b,c=coords;v0=b-a;v1=c-a;d=points-a;den=v0[0]*v1[1]-v0[1]*v1[0]
        if abs(den)<1e-12:continue
        wb=(d[...,0]*v1[1]-d[...,1]*v1[0])/den;wc=(v0[0]*d[...,1]-v0[1]*d[...,0])/den;wa=1-wb-wc
        inside=(wa>=-1e-7)&(wb>=-1e-7)&(wc>=-1e-7)
        world=wa[...,None]*p[0]+wb[...,None]*p[1]+wc[...,None]*p[2]
        inside &= (world[...,0]>=xmin)&(world[...,0]<=xmax)&(world[...,1]>=ymin)&(world[...,1]<=ymax)&(world[...,2]>0.30)
        if not inside.any():continue
        selected+=1
        px=xx[inside];py=yy[inside];w=world[inside]
        dx=np.clip((w[:,0]-xmin)/(xmax-xmin)*(dw-1),0,dw-1)
        dy=np.clip((ymax-w[:,1])/(ymax-ymin)*(dh-1),0,dh-1)
        # Bilinear sample the antialiased artwork across UV islands.
        x0=dx.astype(int);y0=dy.astype(int);x1=np.minimum(x0+1,dw-1);y1=np.minimum(y0+1,dh-1)
        fx=(dx-x0)[:,None];fy=(dy-y0)[:,None]
        sample=(art[y0,x0]*(1-fx)+art[y0,x1]*fx)*(1-fy)+(art[y1,x0]*(1-fx)+art[y1,x1]*fx)*fy
        alpha=sample[:,3:4]/255
        fresh=~surface_mask[py,px]
        # One projection per texel, avoiding double blending at shared triangle edges.
        colors[py[fresh],px[fresh]]=np.rint(sample[fresh,:3]*alpha[fresh]+colors[py[fresh],px[fresh]]*(1-alpha[fresh])).astype('uint8')
        surface_mask[py,px]=True
        mask[py,px] |= sample[:,3]>0
    changed=np.any(colors!=np.asarray(plain.convert('RGB')),axis=2)
    Image.fromarray((mask*255).astype('uint8')).save(out_dir/'dumpster_decal_mask.png')
    metadata={'rectangle':list(DECAL_RECT),'min_front_z':0.30,'min_normal_z':0.7,'mirror':mirror,'font':font,'triangles_projected':selected,'changed_texels':int(changed.sum()),'masked_texels':int(mask.sum())}
    (out_dir/'dumpster_decal.json').write_text(json.dumps(metadata,indent=2)+'\n')
    assert selected>0 and changed.sum()>1000,'decal missed the front panel'
    return Image.fromarray(colors)

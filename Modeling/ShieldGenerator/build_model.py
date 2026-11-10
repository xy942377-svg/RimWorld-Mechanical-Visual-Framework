"""Build the shield-generator geometry with Python 3.10+ and the standard library.
X/Y form the ground plane; Z is up. A corner's emitter faces local +Y.
Four copies are rotated around Z and placed at equal radii. The orb is exported separately.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import primitives as M

COL={'white':(217,216,210),'light':(235,234,227),'dark':(53,60,65),
     'joint':(80,88,93),'black':(24,31,36),'cyan':(0,202,233),
     'amber':(255,180,33),'cyan_rim':(0,153,187),'steel':(120,135,144)}

def rotate(point,degrees):
    a=math.radians(degrees);c,s=math.cos(a),math.sin(a);x,y,z=point
    return (c*x-s*y,s*x+c*y,z)

def transformed(mesh,a=0,shift=(0,0,0),prefix=''):
    # Rotate each vertex in local coordinates, then place the whole part.
    # All placements retain the master mesh's handedness and dimensions.
    return [(tuple(tuple(rotate(v,a)[k]+shift[k] for k in range(3)) for v in p),m,prefix+g)
            for p,m,g in mesh]

def capture(fn):
    M.tris=[];fn();return list(M.tris)

def linspace(a,b,count):
    return [a+(b-a)*i/(count-1) for i in range(count)]

def lathe(profile,mat,group,N=96):
    for (r0,z0),(r1,z1) in zip(profile,profile[1:]):
        for i in range(N):
            a=i*2*math.pi/N;b=(i+1)*2*math.pi/N
            M.quad((r0*math.cos(a),r0*math.sin(a),z0),(r0*math.cos(b),r0*math.sin(b),z0),
                   (r1*math.cos(b),r1*math.sin(b),z1),(r1*math.cos(a),r1*math.sin(a),z1),mat,group)

def sector(profile,a0,a1,mat,group,N=12):
    for (r0,z0),(r1,z1) in zip(profile,profile[1:]):
        for a,b in zip(linspace(a0,a1,N+1)[:-1],linspace(a0,a1,N+1)[1:]):
            M.quad((r0*math.cos(a),r0*math.sin(a),z0),(r0*math.cos(b),r0*math.sin(b),z0),
                   (r1*math.cos(b),r1*math.sin(b),z1),(r1*math.cos(a),r1*math.sin(a),z1),mat,group)
    for a in (a0,a1):
        pts=[(r*math.cos(a),r*math.sin(a),z) for r,z in profile]
        for i in range(1,len(pts)-1):M.tri(pts[0],pts[i],pts[i+1],mat,group)

def build_master():
    # Broad bevelled armor, with one shared front plane and a matching structural back.
    def lean(z):return .13-.25*(z-.55)/1.50
    def shell(x,z0,z1,hx,hy,mat,g,cy=None,b=.04,edge=.04):
        def y(z):return lean(z) if cy is None else cy
        e=min(edge,(z1-z0)*.24,hx*.24,hy*.24)
        M.loft([(z0,x,y(z0),hx-e,hy-e,b*.8),
                (z0+e,x,y(z0+e),hx,hy,b),
                (z1-e,x,y(z1-e),hx,hy,b),
                (z1,x,y(z1),hx-e,hy-e,b*.8)],mat,g)
    M.loft([(0,0,0,.60,.54,.13),(.06,0,0,.65,.59,.14),
            (.20,0,0,.65,.59,.14),(.25,0,0,.61,.55,.13)],'dark','lower_plinth')
    M.loft([(.18,0,0,.60,.54,.12),(.24,0,0,.63,.57,.13),
            (.41,0,0,.63,.57,.13),(.49,0,0,.56,.50,.10)],'white','sculpted_foot')
    M.loft([(.43,0,0,.45,.36,.065),(.49,0,0,.45,.36,.065),
            (.53,0,0,.40,.33,.055)],'dark','recessed_socket')
    for s in (-1,1):
        # Raised frames surround a recessed side vent.
        shell(s*.631,.17,.38,.022,.25,'joint','side_vent_frame',cy=0,b=.008,edge=.008)
        xx=s*.655
        M.quad((xx,-.207,.207),(xx,.207,.207),(xx,.207,.343),(xx,-.207,.343),'black','side_vent')
        for z in (.226,.268,.310):
            xx=s*.659
            M.quad((xx,-.187,z),(xx,.187,z),(xx,.187,z+.014),(xx,-.187,z+.014),'joint','side_louver')
        for yy in (-.40,.40):
            shell(s*.51,.08,.37,.145,.15,'joint','bumper',cy=yy,b=.05,edge=.035)
            shell(s*.51,.34,.49,.14,.145,'white','bumper_cap',cy=yy,b=.05,edge=.025)
            y=yy+math.copysign(.154,yy)
            M.quad((s*.51-.061,y,.241),(s*.51+.061,y,.241),
                   (s*.51+.061,y,.278),(s*.51-.061,y,.278),'amber','corner_marker')
    # The layered emitter panel and both armor rails use the same lean function.
    shell(0,.50,2.01,.275,.155,'dark','spine',b=.035,edge=.035)
    for s in (-1,1):
        x=s*.38
        shell(x,.47,.72,.15,.22,'joint','ankle',b=.04,edge=.035)
        M.loft([(.62,x,lean(.62),.12,.20,.04),(.70,x,lean(.70),.17,.235,.05),
                (1.02,x,lean(1.02),.17,.235,.05),(1.18,x,lean(1.18),.13,.18,.04)],'white','flared_hip')
        shell(x,1.185,2.12,.128,.182,'light','long_cheek',b=.045,edge=.035)
        # An inset vent on the constant-width hip face; never beyond the taper above it.
        xx=s*.551
        ya=lean(.73);yb=lean(.99)
        M.quad((xx,ya-.15,.73),(xx,ya+.15,.73),(xx,yb+.15,.99),(xx,yb-.15,.99),'dark','hip_vent_frame')
        xx=s*.553
        M.quad((xx,ya-.119,.76),(xx,ya+.119,.76),(xx,yb+.119,.96),(xx,yb-.119,.96),'black','hip_vent')
        for z in (.78,.83,.88,.93):
            cy=lean(z);xx=s*.555
            M.quad((xx,cy-.107,z),(xx,cy+.107,z),(xx,cy+.107,z+.015),(xx,cy-.107,z+.015),'joint','hip_louver')
        shell(x,.48,.66,.13,.09,'dark','ankle_front_brace',cy=.31,b=.025,edge=.025)
    # Each emitter panel is a shallow solid on the same inclined plane.
    for i,(z0,z1) in enumerate(((.76,1.10),(1.17,1.51),(1.58,1.92))):
        hx=.262;dy=.192
        M.loft([(z0,0,lean(z0)+dy,hx-.023,.026,.012),
                (z0+.023,0,lean(z0+.023)+dy,hx,.042,.015),
                (z1-.023,0,lean(z1-.023)+dy,hx,.042,.015),
                (z1,0,lean(z1)+dy,hx-.023,.026,.012)],'joint','emitter_slab_'+str(i))
        za=z0+.033;zb=za+.046
        M.quad((-.228,lean(za)+dy+.044,za),(.228,lean(za)+dy+.044,za),
               (.228,lean(zb)+dy+.044,zb),(-.228,lean(zb)+dy+.044,zb),'cyan','emitter_strip_'+str(i))
    # Rear armor: three solid cover sections at precisely the same panel heights.
    for i,(z0,z1) in enumerate(((.76,1.10),(1.17,1.51),(1.58,1.92))):
        M.loft([(z0,0,lean(z0)-.162,.242,.022,.02),
                (z0+.02,0,lean(z0+.02)-.162,.262,.035,.025),
                (z1-.02,0,lean(z1-.02)-.162,.262,.035,.025),
                (z1,0,lean(z1)-.162,.242,.022,.02)],'joint','back_cover_'+str(i))
        for z in (z0+.10,z0+.17,z0+.24):
            M.quad((-.19,lean(z)-.200,z),(.19,lean(z)-.200,z),
                   (.19,lean(z+.025)-.200,z+.025),(-.19,lean(z+.025)-.200,z+.025),'black','back_louver_'+str(i))
    shell(0,1.965,2.085,.253,.183,'joint','upper_crossbeam',b=.028,edge=.02)
    # Front service pod, mechanically nested in the shared foot.
    M.loft([(.29,0,.43,.18,.13,.035),(.53,0,.43,.18,.13,.035),
            (.67,0,.37,.14,.10,.025)],'white','front_service')
    M.box(0,.564,.117,.012,.34,.50,'dark','service_vent_frame',.012)
    M.box(0,.579,.090,.007,.36,.48,'black','service_vent',.007)
    for z in (.38,.42,.46):M.box(0,.588,.078,.005,z,z+.013,'joint','service_louver',.004)
    shell(0,.695,.795,.12,.055,'dark','status_bezel',cy=.30,b=.018,edge=.016)
    M.quad((-.066,.359,.723),(.066,.359,.723),(.066,.359,.761),(-.066,.359,.761),'amber','status_light')
    M.loft([(.32,0,-.41,.17,.12,.03),(.54,0,-.41,.17,.12,.03),
            (.65,0,-.36,.14,.10,.025)],'white','rear_service')
    M.box(0,-.537,.105,.007,.37,.51,'dark','rear_service_vent',.008)
    for z in (.39,.435,.48):M.box(0,-.546,.084,.005,z,z+.014,'joint','rear_service_louver',.005)

# Build the complete corner once; all four placements reuse these local vertices.
MASTER=capture(build_master)

def build_chassis():
    # The continuous base rises directly into the engine and corner load paths.
    M.loft([(0,0,0,1.72,1.72,.38),(.075,0,0,1.78,1.78,.40),
            (.24,0,0,1.78,1.78,.40),(.30,0,0,1.72,1.72,.38)],'dark','foundation')
    M.loft([(.22,0,0,1.67,1.67,.38),(.28,0,0,1.70,1.70,.38),
            (.39,0,0,1.66,1.66,.37)],'white','foundation_shoulder')
    lathe([(1.36,.26),(1.40,.35),(1.40,.60),(1.32,.71),(1.15,.71),(1.15,.40)],'joint','engine_outer_wall')
    lathe([(1.29,.65),(1.25,.72),(.91,.72),(.91,.52)],'black','annular_channel')
    # Raised cylindrical engine, substantial vertical face, recessed cyan aperture.
    lathe([(.89,.47),(.96,.55),(.96,.93),(.90,1.08),(.85,1.15),
           (.66,1.15),(.61,1.09),(.61,.94)],'light','engine_core')
    lathe([(.615,.945),(.595,.965)],'cyan_rim','well_edge')
    lathe([(.595,.963),(0,.963)],'cyan','well_surface')
    lathe([(.96,.54),(.98,.57),(.98,.64),(.955,.67)],'dark','lower_core_band')
    # The outer rim is divided into sections at the radial attachment points.
    for i in range(8):
        a=i*math.pi/4
        sector([(1.40,.57),(1.42,.62),(1.41,.77),(1.34,.84),
                (1.24,.84),(1.205,.78),(1.205,.69)],a+.035,a+math.pi/4-.035,'white','outer_armor_'+str(i))

CHASSIS=capture(build_chassis)

def build_radial_details():
    # Local +Y is radial outward. Repeat the entire sector, never hand-place its faces.
    M.loft([(.26,0,1.43,.235,.27,.045),(.49,0,1.43,.235,.27,.045),
            (.65,0,1.39,.18,.24,.04)],'white','equipment_bay')
    M.box(0,1.710,.155,.014,.32,.49,'black','equipment_bay_vent',.015)
    for z in (.345,.395,.445):M.box(0,1.726,.13,.012,z,z+.018,'joint','equipment_bay_louver',.01)
    M.box(0,1.65,.075,.025,.545,.60,'dark','status_bezel',.01)
    M.box(0,1.68,.048,.006,.558,.582,'amber','status_lamp',.005)
    # Tangential ribs cross the recessed ring and tie it to the central housing.
    M.loft([(.66,0,1.03,.075,.23,.02),(.75,0,1.03,.075,.23,.02),
            (.79,0,1.03,.064,.22,.02)],'joint','channel_crossbrace')
    M.loft([(.56,0,.924,.082,.08,.018),(.90,0,.916,.082,.07,.018),
            (1.075,0,.842,.065,.06,.018)],'white','core_buttress')
    # Recessed central sidewall vent, following its cylindrical envelope.
    a0=math.pi/2-.22;a1=math.pi/2+.22
    sector([(.967,.69),(.967,.89)],a0,a1,'black','core_vent',8)
    for z in (.73,.78,.83):sector([(.972,z),(.972,z+.019)],a0+.025,a1-.025,'joint','core_louver',8)

DETAIL=capture(build_radial_details)
for i in range(8):CHASSIS.extend(transformed(DETAIL,i*45,prefix=f'bay{i}_'))

def build_shoulder():
    M.loft([(.22,0,.91,.30,.31,.06),(.38,0,.91,.30,.31,.06),
            (.57,0,.97,.22,.29,.05)],'joint','load_bridge')
    M.loft([(.53,0,.98,.20,.25,.035),(.63,0,.98,.20,.25,.035),
            (.71,0,.99,.17,.22,.03)],'white','bridge_armor')

SHOULDER=capture(build_shoulder)
ASSEMBLIES=[];BASE=list(CHASSIS)
for i,a in enumerate((45,135,225,315)):
    radial=rotate((0,1.68,0.),a)
    shift=[radial[0],radial[1],0.0]
    instance=transformed(MASTER,a,shift,prefix=f'pylon{i}_')
    BASE.extend(instance)
    BASE.extend(transformed(SHOULDER,a,prefix=f'bridge{i}_'))
    ASSEMBLIES.append({'id':i,'yaw':a,'translation':shift,'mesh':instance})

def make_orb(height=1.60):
    """Sphere vertices are independent of the chassis, so the sphere can move as one part."""
    raw=[];r=.47;N=72;L=36
    for j in range(L):
        ph0=-math.pi/2+j*math.pi/L;ph1=-math.pi/2+(j+1)*math.pi/L
        for i in range(N):
            a=i*2*math.pi/N;b=(i+1)*2*math.pi/N
            ns=[(math.cos(ph)*math.cos(az),math.cos(ph)*math.sin(az),math.sin(ph))
                for ph,az in ((ph0,a),(ph0,b),(ph1,b),(ph1,a))]
            p=[(x*r,y*r,z*r+height) for x,y,z in ns]
            mat='dark' if -math.pi/18<=ph0<0 else ('white' if ph0<0 else 'light')
            for ids in ((0,1,2),(0,2,3)):
                raw.append((tuple(p[k] for k in ids),mat,'orb_shell'))
    def latch():
        M.box(0,-.468,.045,.018,height-.13,height+.04,'joint','orb_latch',.012)
        M.box(0,-.472,.075,.018,height-.13,height-.085,'dark','orb_latch_base',.01)
    raw.extend(capture(latch));return raw

ORB=make_orb()

def valid_face(points):
    a,b,c=points;u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
    cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    return sum(x*x for x in cross)>1e-16

def export_obj(path,mesh):
    """OBJ groups keep vents and armor identifiable. MTL contains plain colors."""
    faces=[t for t in mesh if valid_face(t[0])]
    lines=['mtllib materials.mtl']
    for points,_,_ in faces:
        lines.extend('v '+' '.join(f'{x:.7f}' for x in v) for v in points)
    previous=None
    for i,(_,material,group) in enumerate(faces):
        if (material,group)!=previous:
            lines.extend(('g '+group,'usemtl '+material));previous=(material,group)
        lines.append('f '+' '.join(str(i*3+j+1) for j in range(3)))
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return len(faces)

def validate():
    """Undo each corner's placement and compare every vertex and material to the master."""
    error=0.0
    for inst in ASSEMBLIES:
        restored=transformed(inst['mesh'],shift=tuple(-v for v in inst['translation']))
        restored=transformed(restored,-inst['yaw'])
        if len(restored)!=len(MASTER):raise ValueError('A corner has a different triangle count from the shared master.')
        for (points,material,_),(ref,ref_material,_) in zip(restored,MASTER):
            if material!=ref_material:raise ValueError('A corner uses a different material from the corresponding master triangle.')
            error=max(error,max(abs(a-b) for v,w in zip(points,ref) for a,b in zip(v,w)))
    if error>1e-10:raise ValueError('After reversing placement, corner vertices differ from the shared master by more than 1e-10.')
    for mesh in (BASE,ORB):
        if any(not math.isfinite(x) for p,_,_ in mesh for v in p for x in v):
            raise ValueError('A vertex coordinate is NaN or infinity.')
    return {'cornerAngles':[x['yaw'] for x in ASSEMBLIES],
            'cornerRadius':1.68,'cornerScale':1.0,'maxInverseTransformError':error,
            'masterFaces':len(MASTER),'baseFaces':len(BASE),'orbFaces':len(ORB),
            'camera':{'projection':'orthographic','elevationDegrees':55},
            'instances':[{k:v for k,v in x.items() if k!='mesh'} for x in ASSEMBLIES]}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[2]/'Work/ShieldModel')
    args=parser.parse_args();out=args.output
    # Export into an empty directory so existing model files remain available.
    if out.exists() and any(out.iterdir()):parser.error('output folder must be empty')
    report=validate();out.mkdir(parents=True,exist_ok=True)
    counts={}
    for name,mesh in (('shared_corner',MASTER),('shield_base',BASE),('orb',ORB)):
        counts[name]=export_obj(out/(name+'.obj'),mesh)
    lines=[]
    for name,color in COL.items():
        lines.extend(('newmtl '+name,'Kd '+' '.join(f'{x/255:.5f}' for x in color)))
        if name in ('cyan','amber','cyan_rim'):lines.append('Ke '+' '.join(f'{x/255:.5f}' for x in color))
    (out/'materials.mtl').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    report['exportedFaces']=counts
    report['files']={f.name:hashlib.sha256(f.read_bytes()).hexdigest()
                     for f in sorted(out.iterdir()) if f.is_file()}
    (out/'structure-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS four rotated copies of one corner; separate base and orb')
    print('Exported triangles:',counts)
    print('Output:',out)

if __name__=='__main__':main()

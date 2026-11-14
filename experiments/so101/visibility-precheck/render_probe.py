from pathlib import Path
import sys,json,hashlib
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import numpy as np
import mujoco
from PIL import Image,ImageDraw
from simulation.so101.scene import load_scene,reset_scene,JOINT_NAMES,ObjectPlacement,DEFAULT_PLACEMENT,evaluate_placement,DEFAULT_SCENE
root=ROOT;out=root/'experiments/so101/visibility-precheck';out.mkdir(parents=True,exist_ok=True)
m,d=load_scene();r=mujoco.Renderer(m,256,256)
addr=np.array([m.jnt_qposadr[m.joint(n).id] for n in JOINT_NAMES]);rng=np.random.default_rng(20261114)
qs=np.zeros((240,6));qs[:,:5]=rng.uniform([-1.2,-1,-1.3,-1.4,-1],[1.2,1,1.3,1.4,1],(240,5));qs[:,5]=.4;qs[0]=0
robot_bodies={m.body(n).id for n in ['base','shoulder','upper_arm','lower_arm','wrist','gripper','moving_jaw_so101_v1']};moving=robot_bodies-{m.body('base').id}
visible=mujoco.MjvOption();hidden=mujoco.MjvOption();hidden.geomgroup[2:4]=0
objid=m.geom('red_object_geom').id;geometry=int(mujoco.mjtObj.mjOBJ_GEOM)
records=[];selected=[]
for label in [False,True]:
 placement=DEFAULT_PLACEMENT if not label else ObjectPlacement(red=(.28,0,.041),blue=DEFAULT_PLACEMENT.blue,goal=DEFAULT_PLACEMENT.goal)
 valid=[]
 for i,q in enumerate(qs):
  reset_scene(m,d,placement=placement);d.qpos[addr]=q;mujoco.mj_forward(m,d)
  bad=[]
  for c in d.contact:
   b1=int(m.geom_bodyid[c.geom1]);b2=int(m.geom_bodyid[c.geom2])
   if c.dist<0 and (b1 in moving or b2 in moving):bad.append([int(c.geom1),int(c.geom2),float(c.dist)])
  if bad:continue
  assert evaluate_placement(m,d,'red')==label
  for cam in ['front_camera','overhead_camera']:
   counts=[]
   for opt in [visible,hidden]:
    r.enable_segmentation_rendering();r.update_scene(d,camera=cam,scene_option=opt);s=r.render();counts.append(int(((s[:,:,0]==objid)&(s[:,:,1]==geometry)).sum()))
   if not counts[1]:continue
   rec={'q_index':i,'label_placement_success':label,'q_rad':q.tolist(),'camera':cam,'visible_red_pixels':counts[0],'red_pixels_without_rendered_robot':counts[1],'visibility_fraction':counts[0]/counts[1],'object_poses':{'red':list(placement.red),'blue':list(placement.blue)},'negative_distance_contacts_involving_moving_robot':0}
   records.append(rec);valid.append(rec)
 for cam in ['front_camera','overhead_camera']:
  subset=[v for v in valid if v['camera']==cam]
  if not subset:continue
  for mode,rec in [('occluded',min(subset,key=lambda v:v['visibility_fraction'])),('visible',max(subset,key=lambda v:v['visibility_fraction']))]:
   reset_scene(m,d,placement=placement);d.qpos[addr]=rec['q_rad'];mujoco.mj_forward(m,d);r.disable_segmentation_rendering();r.update_scene(d,camera=cam,scene_option=visible);img=r.render().copy()
   name=f"{'success' if label else 'failure'}_{cam}_{mode}.png";Image.fromarray(img).save(out/name);selected.append({**rec,'selection':mode,'image':name})
r.close()
summary={'kind':'static_scene_render_feasibility_not_a_policy_or_reward_model_experiment','seed':20261114,'mujoco_version':mujoco.__version__,'scene_sha256':hashlib.sha256(DEFAULT_SCENE.read_bytes()).hexdigest(),'sampled_robot_configurations_per_object_state':len(qs),'object_states':2,'records':records,'selected':selected,'selection_rule':'For each true object predicate and camera, choose min/max red-object pixel visibility among sampled configurations with no negative-distance contact involving moving robot; static configurations only.','limitations':['No task execution or collision-free connecting motion was tested.','Object states were reset directly, not reached by a policy.','No reward-model scores, false completion or optimization exploitation was measured.','Same object state does not imply same future action value; only current stable-placement predicate is fixed.','Geometric visibility change alone is not evidence of model failure or method novelty.']}
(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
canvas=Image.new('RGB',(256*4,286*2),'white');draw=ImageDraw.Draw(canvas)
for k,rec in enumerate(selected):
 x=(k%4)*256;y=(k//4)*286;canvas.paste(Image.open(out/rec['image']),(x,y));draw.text((x+4,y+258),f"Y={int(rec['label_placement_success'])} {rec['camera']} {rec['selection']}",fill='black');draw.text((x+4,y+272),f"visible={rec['visibility_fraction']:.3f}",fill='black')
canvas.save(out/'contact-sheet.png')
print(json.dumps({'records':len(records),'selected':[{k:v[k] for k in ['label_placement_success','camera','selection','visibility_fraction','q_index']} for v in selected]},ensure_ascii=False),flush=True)

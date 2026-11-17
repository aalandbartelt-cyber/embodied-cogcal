/* Browser-side MuJoCo viewer for the research console.
 *
 * MuJoCo 4 compiled to WebAssembly performs the forward kinematics; three.js
 * draws the geoms at 60 fps.  Nothing is pre-rendered and nothing is faked: the
 * mesh geometry comes from MuJoCo's own parsed model and the pose comes from
 * the recorded joint angles.
 */
const status = { ready: false, error: null, nq: null, geoms: 0 };
let mujoco = null, model = null, data = null;
let three = null, renderer = null, scene = null, camera = null, controls = null;
let geoms = [];
let host = null;
let pending = null;   // { joints, objectPos }
let dirty = true;

const asView = (value) => (value && typeof value.GetView === 'function') ? value.GetView() : value;

function setScalar(array, index, value) {
  if (!array) return;
  if (typeof array.Set === 'function') { array.Set(index, value); return; }
  if (array.GetView) { array.GetView()[index] = value; return; }
  array[index] = value;
}

function readScalar(array, index) {
  if (!array) return 0;
  if (array.GetView) return array.GetView()[index];
  return array[index];
}

function meshGeometry(meshId) {
  const vertAdr = readScalar(model.mesh_vertadr, meshId);
  const vertNum = readScalar(model.mesh_vertnum, meshId);
  const faceAdr = readScalar(model.mesh_faceadr, meshId);
  const faceNum = readScalar(model.mesh_facenum, meshId);
  const verts = asView(model.mesh_vert);
  const faces = asView(model.mesh_face);
  const geometry = new three.BufferGeometry();
  const positions = new Float32Array(vertNum * 3);
  for (let i = 0; i < vertNum * 3; i += 1) positions[i] = verts[vertAdr * 3 + i];
  const indices = new Uint32Array(faceNum * 3);
  for (let i = 0; i < faceNum * 3; i += 1) indices[i] = faces[faceAdr * 3 + i];
  geometry.setAttribute('position', new three.BufferAttribute(positions, 3));
  geometry.setIndex(new three.BufferAttribute(indices, 1));
  geometry.computeVertexNormals();
  return geometry;
}

function geomObject(index) {
  const type = readScalar(model.geom_type, index);
  const size = asView(model.geom_size);
  const sx = size[index * 3], sy = size[index * 3 + 1], sz = size[index * 3 + 2];
  let geometry;
  if (type === 7) {                       // mjGEOM_MESH
    geometry = meshGeometry(readScalar(model.geom_dataid, index));
  } else if (type === 6) {                // box: size = half extents
    geometry = new three.BoxGeometry(sx * 2, sy * 2, sz * 2);
  } else if (type === 5) {                // cylinder
    geometry = new three.CylinderGeometry(sx, sx, sy * 2, 28);
    geometry.rotateX(Math.PI / 2);
  } else if (type === 3) {                // capsule
    geometry = new three.CapsuleGeometry(sx, sy * 2, 8, 20);
    geometry.rotateX(Math.PI / 2);
  } else if (type === 2) {                // sphere
    geometry = new three.SphereGeometry(sx, 24, 16);
  } else if (type === 0) {                // plane (XY plane is the floor for Z-up)
    geometry = new three.PlaneGeometry(3.2, 3.2);
  } else {
    return null;
  }
  const geomRgba = asView(model.geom_rgba);
  const matId = readScalar(model.geom_matid, index);
  const matRgba = asView(model.mat_rgba);
  const source = (matId >= 0 && matRgba) ? matRgba : geomRgba;
  const base = (matId >= 0 && matRgba) ? matId : index;
  const r = source[base * 4], g = source[base * 4 + 1], b = source[base * 4 + 2], a = source[base * 4 + 3];
  const color = new three.Color(
    Number.isFinite(r) ? r : 0.6, Number.isFinite(g) ? g : 0.6, Number.isFinite(b) ? b : 0.6);
  const opacity = Number.isFinite(a) && a > 0.01 ? a : 1;
  const material = new three.MeshStandardMaterial({
    color, roughness: 0.55, metalness: 0.12,
    transparent: opacity < 0.999, opacity,
    side: type === 0 ? three.DoubleSide : three.FrontSide,
  });
  const mesh = new three.Mesh(geometry, material);
  mesh.matrixAutoUpdate = false;
  mesh.userData.index = index;
  return mesh;
}

function syncGeoms() {
  const pos = asView(data.geom_xpos);
  const mat = asView(data.geom_xmat);
  for (const mesh of geoms) {
    const i = mesh.userData.index;
    const m = mesh.matrix.elements;
    m[0] = mat[i * 9]; m[1] = mat[i * 9 + 3]; m[2] = mat[i * 9 + 6]; m[3] = 0;
    m[4] = mat[i * 9 + 1]; m[5] = mat[i * 9 + 4]; m[6] = mat[i * 9 + 7]; m[7] = 0;
    m[8] = mat[i * 9 + 2]; m[9] = mat[i * 9 + 5]; m[10] = mat[i * 9 + 8]; m[11] = 0;
    m[12] = pos[i * 3]; m[13] = pos[i * 3 + 1]; m[14] = pos[i * 3 + 2]; m[15] = 1;
    mesh.matrixWorldNeedsUpdate = true;
  }
}

function applyPending() {
  if (!pending) return;
  const { joints, objectPos } = pending;
  const qpos = 6;
  for (let i = 0; i < Math.min(joints.length, qpos); i += 1) {
    const value = joints[i];
    if (typeof value === 'number' && Number.isFinite(value)) setScalar(data.qpos, i, value);
  }
  if (objectPos) {
    // red_object free joint: 3 position values then an identity quaternion
    for (let i = 0; i < 3; i += 1) setScalar(data.qpos, qpos + i, objectPos[i]);
    setScalar(data.qpos, qpos + 3, 1);
    setScalar(data.qpos, qpos + 4, 0);
    setScalar(data.qpos, qpos + 5, 0);
    setScalar(data.qpos, qpos + 6, 0);
  }
  mujoco.mj_forward(model, data);
  syncGeoms();
  dirty = false;
}

function resize() {
  if (!renderer || !host) return;
  const width = host.clientWidth || 640;
  const height = host.clientHeight || 400;
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

function loop() {
  requestAnimationFrame(loop);
  if (!renderer) return;
  if (dirty) {
    try {
      applyPending();
    } catch (error) {
      status.error = String(error);
    }
  }
  controls.update();
  renderer.render(scene, camera);
}

async function boot(element) {
  host = element;
  three = await import('three');
  const { OrbitControls } = await import('/vendor/three/OrbitControls.js');
  const module = await import('/vendor/mujoco/mujoco.js');
  mujoco = await module.default();

  const xml = await (await fetch('/api/mj-asset?name=scene')).text();
  const names = [...new Set([...xml.matchAll(/file="([^"]+)"/g)].map((match) => match[1])
    .filter((name) => /\.(stl|obj|png)$/i.test(name)))];
  const vfs = new mujoco.MjVFS();
  for (const name of names) {
    const response = await fetch('/api/mj-asset?name=' + encodeURIComponent(name));
    if (!response.ok) throw new Error('缺少网格文件：' + name);
    vfs.addBuffer('assets/' + name, new Uint8Array(await response.arrayBuffer()));
  }
  model = mujoco.MjModel.from_xml_string(xml, vfs);
  data = new mujoco.MjData(model);
  mujoco.mj_forward(model, data);

  renderer = new three.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = three.PCFSoftShadowMap;
  host.replaceChildren(renderer.domElement);

  scene = new three.Scene();
  scene.background = new three.Color(0x0c1512);
  camera = new three.PerspectiveCamera(45, 1, 0.01, 50);
  camera.up.set(0, 0, 1);   // MuJoCo is Z-up
  camera.position.set(0.50, -0.46, 0.34);

  const hemi = new three.HemisphereLight(0xcfe3d6, 0x0a1512, 0.55);
  scene.add(hemi);
  const key = new three.DirectionalLight(0xffffff, 1.25);
  key.position.set(0.9, -1.1, 1.8);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  key.shadow.camera.left = -1.2; key.shadow.camera.right = 1.2;
  key.shadow.camera.top = 1.2; key.shadow.camera.bottom = -1.2;
  scene.add(key);
  scene.add(new three.AmbientLight(0xffffff, 0.22));

  for (let i = 0; i < model.ngeom; i += 1) {
    const mesh = geomObject(i);
    if (!mesh) continue;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    scene.add(mesh);
    geoms.push(mesh);
  }

  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0.16, 0.0, 0.10);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.minDistance = 0.35;
  controls.maxDistance = 3.0;
  controls.update();

  resize();
  window.addEventListener('resize', resize);
  status.ready = true;
  status.nq = model.nq;
  status.geoms = geoms.length;
  syncGeoms();
  loop();
  return status;
}

window.WBSim = {
  status,
  setPose(joints, objectPos) {
    pending = { joints: joints || [], objectPos: objectPos || null };
    dirty = true;
  },
  resetView() {
    if (!camera || !controls) return;
    camera.position.set(0.50, -0.46, 0.34);
    controls.target.set(0.18, 0.0, 0.12);
    controls.update();
  },
  boot,
};

window.WBSimReady = boot(document.getElementById('sim-canvas')).catch((error) => {
  status.error = String(error && error.message ? error.message : error);
  const box = document.getElementById('sim-error');
  if (box) { box.textContent = 'MuJoCo WASM 加载失败：' + status.error; box.hidden = false; }
  return status;
});

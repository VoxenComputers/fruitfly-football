/**
 * Drosophila Connectome SNN - 5v5 Fly Football Championship
 * Sunny Day Grassland Arena with Spacious Stadium & Perimeter Trees.
 * Team Red vs Team Blue on 48x28 Stadium Pitch.
 * Interactive Fly Selection, Real-Time Nervous / Arousal & Biometric Telemetry,
 * and Precision Goal Scoring & Formation Reset.
 */

(function () {
  "use strict";

  // --- 1. Scene, Sky & Sunny Day Lighting ---
  const container = document.getElementById("canvas-container");
  const scene = new THREE.Scene();

  // Bright sunny daytime sky
  const skyColor = new THREE.Color(0x9bd7f7);
  scene.background = skyColor;
  scene.fog = new THREE.Fog(0xc5e7f9, 45, 145);

  const camera = new THREE.PerspectiveCamera(
    42,
    window.innerWidth / window.innerHeight,
    0.1,
    300
  );
  camera.position.set(0, 24, 34);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.maxDistance = 90;
  controls.minDistance = 5;
  controls.target.set(0, 0.8, 0);

  // Sunny Lighting
  const ambientLight = new THREE.AmbientLight(0xfff8ee, 1.3);
  scene.add(ambientLight);

  // Warm golden sun
  const sunLight = new THREE.DirectionalLight(0xfff5dd, 2.3);
  sunLight.position.set(30, 48, 26);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.width = 2048;
  sunLight.shadow.mapSize.height = 2048;
  sunLight.shadow.camera.near = 1;
  sunLight.shadow.camera.far = 140;
  sunLight.shadow.camera.left = -35;
  sunLight.shadow.camera.right = 35;
  sunLight.shadow.camera.top = 30;
  sunLight.shadow.camera.bottom = -30;
  sunLight.shadow.bias = -0.0004;
  scene.add(sunLight);

  // Sky blue fill light
  const skyFill = new THREE.DirectionalLight(0xaad8f5, 0.7);
  skyFill.position.set(-25, 30, -25);
  scene.add(skyFill);

  // --- 2. Sunny Grassland & Perimeter Trees (Spacious Stadium) ---
  const meadowGeo = new THREE.PlaneGeometry(240, 240);
  const meadowMat = new THREE.MeshStandardMaterial({
    color: 0x5eb84c,
    roughness: 0.85,
  });
  const meadow = new THREE.Mesh(meadowGeo, meadowMat);
  meadow.rotation.x = -Math.PI / 2;
  meadow.position.y = -0.02;
  meadow.receiveShadow = true;
  scene.add(meadow);

  // Low-Poly 3D Trees Outside the Pitch Perimeter
  function createTree(scale = 1.0) {
    const tree = new THREE.Group();

    // Wooden trunk
    const trunkGeo = new THREE.CylinderGeometry(0.22 * scale, 0.3 * scale, 2.0 * scale, 6);
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x5a4128, roughness: 0.85 });
    const trunk = new THREE.Mesh(trunkGeo, trunkMat);
    trunk.position.y = (2.0 * scale) / 2;
    trunk.castShadow = true;
    tree.add(trunk);

    // 3 Tiers of lush green foliage
    const foliageMat = new THREE.MeshStandardMaterial({
      color: Math.random() < 0.5 ? 0x3b8535 : 0x489642,
      roughness: 0.65,
      flatShading: true,
    });

    for (let i = 0; i < 3; i++) {
      const coneR = (1.4 - i * 0.3) * scale;
      const coneH = (1.6 - i * 0.18) * scale;
      const cone = new THREE.Mesh(new THREE.ConeGeometry(coneR, coneH, 7), foliageMat);
      cone.position.y = (1.4 + i * 0.85) * scale;
      cone.rotation.y = i * 0.5;
      cone.castShadow = true;
      tree.add(cone);
    }

    return tree;
  }

  // Position trees naturally beyond the pitch perimeter
  const treePositions = [];
  // Top border (Z < -19)
  for (let x = -48; x <= 48; x += 6.5) {
    treePositions.push([x + (Math.random() - 0.5) * 3, -20 - Math.random() * 12]);
    treePositions.push([x + (Math.random() - 0.5) * 3, -32 - Math.random() * 16]);
  }
  // Bottom border (Z > 19)
  for (let x = -48; x <= 48; x += 6.5) {
    treePositions.push([x + (Math.random() - 0.5) * 3, 20 + Math.random() * 12]);
    treePositions.push([x + (Math.random() - 0.5) * 3, 32 + Math.random() * 16]);
  }
  // Left border (X < -30)
  for (let z = -20; z <= 20; z += 6.5) {
    treePositions.push([-32 - Math.random() * 12, z + (Math.random() - 0.5) * 3]);
  }
  // Right border (X > 30)
  for (let z = -20; z <= 20; z += 6.5) {
    treePositions.push([32 + Math.random() * 12, z + (Math.random() - 0.5) * 3]);
  }

  treePositions.forEach(([tx, tz]) => {
    const scale = 1.0 + Math.random() * 0.7;
    const tree = createTree(scale);
    tree.position.set(tx, 0, tz);
    tree.rotation.y = Math.random() * Math.PI * 2;
    scene.add(tree);
  });

  // --- 3. Enlarged Stadium Pitch (48.0 x 28.0 units) ---
  const pitchL = 48.0;
  const pitchW = 28.0;
  const pitchHalfL = pitchL / 2; // 24.0
  const pitchHalfW = pitchW / 2; // 14.0
  const goalWidth = 5.8;
  const goalHeight = 2.5;

  const pitchGroup = new THREE.Group();
  scene.add(pitchGroup);

  // Mowed Lawn Striped Pattern (16 stripes)
  const numStripes = 16;
  const stripeW = pitchL / numStripes;
  const grassMat1 = new THREE.MeshStandardMaterial({ color: 0x48a838, roughness: 0.7 });
  const grassMat2 = new THREE.MeshStandardMaterial({ color: 0x3fa02f, roughness: 0.7 });

  for (let i = 0; i < numStripes; i++) {
    const sGeo = new THREE.PlaneGeometry(stripeW, pitchW);
    const stripe = new THREE.Mesh(sGeo, i % 2 === 0 ? grassMat1 : grassMat2);
    stripe.rotation.x = -Math.PI / 2;
    stripe.position.set(-pitchHalfL + stripeW * i + stripeW / 2, 0.005, 0);
    stripe.receiveShadow = true;
    pitchGroup.add(stripe);
  }

  // Pitch Boundary Lines
  const lineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });

  function addPitchLine(w, h, x, z) {
    const lGeo = new THREE.PlaneGeometry(w, h);
    const line = new THREE.Mesh(lGeo, lineMat);
    line.rotation.x = -Math.PI / 2;
    line.position.set(x, 0.012, z);
    pitchGroup.add(line);
  }

  const lw = 0.16; // Line width
  // Touchlines & Goal lines
  addPitchLine(pitchL, lw, 0, -pitchHalfW);
  addPitchLine(pitchL, lw, 0, pitchHalfW);
  addPitchLine(lw, pitchW, -pitchHalfL, 0);
  addPitchLine(lw, pitchW, pitchHalfL, 0);
  // Halfway line
  addPitchLine(lw, pitchW, 0, 0);

  // Center Circle
  const centerCircle = new THREE.Mesh(
    new THREE.RingGeometry(4.2 - lw / 2, 4.2 + lw / 2, 48),
    lineMat
  );
  centerCircle.rotation.x = -Math.PI / 2;
  centerCircle.position.set(0, 0.013, 0);
  pitchGroup.add(centerCircle);

  // Center Spot
  const centerSpot = new THREE.Mesh(new THREE.CircleGeometry(0.25, 24), lineMat);
  centerSpot.rotation.x = -Math.PI / 2;
  centerSpot.position.set(0, 0.014, 0);
  pitchGroup.add(centerSpot);

  // Penalty Boxes (Left & Right)
  const boxDepth = 7.5;
  const boxWidth = 14.0;
  // Left Box
  addPitchLine(boxDepth, lw, -pitchHalfL + boxDepth / 2, -boxWidth / 2);
  addPitchLine(boxDepth, lw, -pitchHalfL + boxDepth / 2, boxWidth / 2);
  addPitchLine(lw, boxWidth, -pitchHalfL + boxDepth, 0);
  // Right Box
  addPitchLine(boxDepth, lw, pitchHalfL - boxDepth / 2, -boxWidth / 2);
  addPitchLine(boxDepth, lw, pitchHalfL - boxDepth / 2, boxWidth / 2);
  addPitchLine(lw, boxWidth, pitchHalfL - boxDepth, 0);

  // 3D White Goalposts with Nets
  function createGoalpost() {
    const goal = new THREE.Group();
    const postMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
    const postGeo = new THREE.CylinderGeometry(0.09, 0.09, goalHeight, 16);

    // Left post
    const pLeft = new THREE.Mesh(postGeo, postMat);
    pLeft.position.set(0, goalHeight / 2, -goalWidth / 2);
    pLeft.castShadow = true;
    goal.add(pLeft);

    // Right post
    const pRight = new THREE.Mesh(postGeo, postMat);
    pRight.position.set(0, goalHeight / 2, goalWidth / 2);
    pRight.castShadow = true;
    goal.add(pRight);

    // Crossbar
    const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, goalWidth, 16), postMat);
    bar.rotation.x = Math.PI / 2;
    bar.position.set(0, goalHeight, 0);
    bar.castShadow = true;
    goal.add(bar);

    // Net (Positioned outside the pitch behind the goal line)
    const netMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      wireframe: true,
      transparent: true,
      opacity: 0.35,
    });
    const net = new THREE.Mesh(new THREE.BoxGeometry(1.8, goalHeight, goalWidth), netMat);
    net.position.set(0.9, goalHeight / 2, 0);
    goal.add(net);

    return goal;
  }

  const redGoal = createGoalpost();
  redGoal.position.set(-pitchHalfL, 0, 0);
  redGoal.rotation.y = Math.PI;
  scene.add(redGoal);

  const blueGoal = createGoalpost();
  blueGoal.position.set(pitchHalfL, 0, 0);
  scene.add(blueGoal);

  // --- Perimeter LED Advertising Boards ---
  function createAdBoard(w, text, colorHex) {
    const group = new THREE.Group();
    const boardMat = new THREE.MeshStandardMaterial({ color: 0x111620, roughness: 0.4 });
    const board = new THREE.Mesh(new THREE.BoxGeometry(w, 0.7, 0.15), boardMat);
    board.position.y = 0.35;
    board.castShadow = true;
    group.add(board);

    const neonMat = new THREE.MeshBasicMaterial({ color: colorHex });
    const neon = new THREE.Mesh(new THREE.BoxGeometry(w, 0.05, 0.16), neonMat);
    neon.position.y = 0.7;
    group.add(neon);
    return group;
  }

  const adTop = createAdBoard(pitchL + 4, "WORLD CONNECTOME CUP • TEAM RED vs TEAM BLUE", 0xd8ff00);
  adTop.position.set(0, 0, -pitchHalfW - 1.4);
  scene.add(adTop);

  const adBottom = createAdBoard(pitchL + 4, "DROSOPHILA 5v5 SNN CHAMPIONSHIP", 0xd8ff00);
  adBottom.position.set(0, 0, pitchHalfW + 1.4);
  scene.add(adBottom);

  const adLeftTop = createAdBoard(9.0, "TEAM RED DEFENSE", 0xff3344);
  adLeftTop.rotation.y = Math.PI / 2;
  adLeftTop.position.set(-pitchHalfL - 1.4, 0, -9.0);
  scene.add(adLeftTop);

  const adLeftBottom = createAdBoard(9.0, "TEAM RED DEFENSE", 0xff3344);
  adLeftBottom.rotation.y = Math.PI / 2;
  adLeftBottom.position.set(-pitchHalfL - 1.4, 0, 9.0);
  scene.add(adLeftBottom);

  const adRightTop = createAdBoard(9.0, "TEAM BLUE DEFENSE", 0x0088ff);
  adRightTop.rotation.y = -Math.PI / 2;
  adRightTop.position.set(pitchHalfL + 1.4, 0, -9.0);
  scene.add(adRightTop);

  const adRightBottom = createAdBoard(9.0, "TEAM BLUE DEFENSE", 0x0088ff);
  adRightBottom.rotation.y = -Math.PI / 2;
  adRightBottom.position.set(pitchHalfL + 1.4, 0, 9.0);
  scene.add(adRightBottom);

  // Corner Flags
  function createCornerFlag(flagColorHex) {
    const flagGroup = new THREE.Group();
    const poleMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 });
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.4, 8), poleMat);
    pole.position.y = 0.7;
    flagGroup.add(pole);

    const clothMat = new THREE.MeshStandardMaterial({
      color: flagColorHex,
      roughness: 0.5,
      side: THREE.DoubleSide,
    });
    const cloth = new THREE.Mesh(new THREE.PlaneGeometry(0.35, 0.25), clothMat);
    cloth.position.set(0.18, 1.25, 0);
    flagGroup.add(cloth);
    return flagGroup;
  }

  const flagTL = createCornerFlag(0xff3344); flagTL.position.set(-pitchHalfL, 0, -pitchHalfW); scene.add(flagTL);
  const flagBL = createCornerFlag(0xff3344); flagBL.position.set(-pitchHalfL, 0, pitchHalfW); scene.add(flagBL);
  const flagTR = createCornerFlag(0x0088ff); flagTR.position.set(pitchHalfL, 0, -pitchHalfW); scene.add(flagTR);
  const flagBR = createCornerFlag(0x0088ff); flagBR.position.set(pitchHalfL, 0, pitchHalfW); scene.add(flagBR);

  // Corner Stadium Floodlight Towers
  function createFloodlightTower() {
    const tower = new THREE.Group();
    const metalMat = new THREE.MeshStandardMaterial({ color: 0x3a424e, metalness: 0.6, roughness: 0.4 });
    const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.35, 14, 8), metalMat);
    mast.position.y = 7;
    mast.castShadow = true;
    tower.add(mast);

    const head = new THREE.Mesh(new THREE.BoxGeometry(2.0, 1.2, 0.6), metalMat);
    head.position.set(0, 14, 0);
    head.rotation.x = 0.35;
    tower.add(head);

    const lightFace = new THREE.Mesh(
      new THREE.PlaneGeometry(1.8, 1.0),
      new THREE.MeshBasicMaterial({ color: 0xffffff })
    );
    lightFace.position.set(0, 14, 0.32);
    lightFace.rotation.x = 0.35;
    tower.add(lightFace);
    return tower;
  }

  const towerPositions = [
    [-pitchHalfL - 4.5, -pitchHalfW - 3.5, 0.4],
    [-pitchHalfL - 4.5, pitchHalfW + 3.5, -0.4],
    [pitchHalfL + 4.5, -pitchHalfW - 3.5, 0.4 + Math.PI],
    [pitchHalfL + 4.5, pitchHalfW + 3.5, -0.4 + Math.PI],
  ];
  towerPositions.forEach(([x, z, ry]) => {
    const t = createFloodlightTower();
    t.position.set(x, 0, z);
    t.rotation.y = ry;
    scene.add(t);
  });

  // --- 4. 3D Soccer Ball with Physical Simulation ---
  const ballRadius = 0.42;
  const ballCanvas = document.createElement("canvas");
  ballCanvas.width = 512;
  ballCanvas.height = 256;
  const bctx = ballCanvas.getContext("2d");
  bctx.fillStyle = "#ffffff";
  bctx.fillRect(0, 0, 512, 256);
  bctx.fillStyle = "#111111";
  for (let r = 0; r < 5; r++) {
    for (let c = 0; c < 10; c++) {
      if ((r + c) % 2 === 0) {
        bctx.beginPath();
        bctx.arc(c * 52 + 26, r * 52 + 26, 19, 0, Math.PI * 2);
        bctx.fill();
      }
    }
  }
  const ballTex = new THREE.CanvasTexture(ballCanvas);
  const ballMesh = new THREE.Mesh(
    new THREE.SphereGeometry(ballRadius, 32, 32),
    new THREE.MeshStandardMaterial({ map: ballTex, roughness: 0.25 })
  );
  ballMesh.castShadow = true;
  scene.add(ballMesh);

  const ball = {
    pos: new THREE.Vector3(0, ballRadius + 0.05, 0),
    vel: new THREE.Vector3(0, 0, 0),
    radius: ballRadius,
  };

  function resetBall(kickoffTeam = "RED") {
    ball.pos.set(0, ballRadius + 0.05, 0);
    const sign = kickoffTeam === "RED" ? 1 : -1;
    ball.vel.set(sign * (Math.random() * 2.2 + 1.5), 0.5, (Math.random() - 0.5) * 2.0);
  }
  resetBall("RED");

  // --- 5. Procedural Low-Poly Fly Generator (RED EYES vs BLUE EYES) ---
  const bristleMat = new THREE.MeshStandardMaterial({ color: 0x111316, roughness: 0.8 });

  function createFlyModel(eyeColorHex, teamColorHex) {
    const fly = new THREE.Group();

    // Body Chitin (Faceted low-poly)
    const chitinMat = new THREE.MeshStandardMaterial({
      color: 0x2e353d,
      roughness: 0.45,
      flatShading: true,
    });

    // Thorax
    const thorax = new THREE.Mesh(new THREE.IcosahedronGeometry(0.4, 1), chitinMat);
    thorax.scale.set(0.85, 0.95, 1.3);
    thorax.castShadow = true;
    fly.add(thorax);

    // Dorsal Micro-Bristles
    const bristleGeo = new THREE.ConeGeometry(0.015, 0.2, 4);
    [
      [-0.14, 0.34, -0.1], [0.14, 0.34, -0.1],
      [-0.18, 0.32, 0.1], [0.18, 0.32, 0.1],
      [0.0, 0.38, 0.0], [0.0, 0.38, 0.22],
      [-0.12, 0.32, 0.24], [0.12, 0.32, 0.24]
    ].forEach(([bx, by, bz]) => {
      const b = new THREE.Mesh(bristleGeo, bristleMat);
      b.position.set(bx, by, bz);
      b.rotation.z = -bx * 1.5;
      fly.add(b);
    });

    // Abdomen
    const abdomen = new THREE.Mesh(new THREE.ConeGeometry(0.36, 1.05, 7), chitinMat);
    abdomen.scale.set(0.8, 1.0, 0.75);
    abdomen.rotation.x = Math.PI / 1.8;
    abdomen.position.set(0, -0.05, -0.65);
    abdomen.castShadow = true;
    fly.add(abdomen);

    // Head
    const headGroup = new THREE.Group();
    headGroup.position.set(0, 0.12, 0.52);
    fly.add(headGroup);

    const head = new THREE.Mesh(
      new THREE.IcosahedronGeometry(0.25, 1),
      new THREE.MeshStandardMaterial({ color: 0x4a5563, flatShading: true })
    );
    headGroup.add(head);

    // Team Collar
    const collar = new THREE.Mesh(
      new THREE.TorusGeometry(0.14, 0.04, 8, 20),
      new THREE.MeshStandardMaterial({
        color: teamColorHex,
        emissive: teamColorHex,
        emissiveIntensity: 0.6,
      })
    );
    collar.rotation.x = Math.PI / 2.5;
    collar.position.set(0, 0.09, -0.05);
    headGroup.add(collar);

    // Compound Eyes (RED EYES FOR TEAM RED, BLUE EYES FOR TEAM BLUE)
    const eyeMat = new THREE.MeshPhysicalMaterial({
      color: eyeColorHex,
      emissive: eyeColorHex,
      emissiveIntensity: 0.75,
      roughness: 0.1,
      metalness: 0.2,
      clearcoat: 1.0,
    });
    const eyeGeo = new THREE.SphereGeometry(0.16, 16, 16);

    const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    leftEye.position.set(-0.18, 0.02, 0.05);
    headGroup.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye.position.set(0.18, 0.02, 0.05);
    headGroup.add(rightEye);

    // Wings
    const wingMat = new THREE.MeshStandardMaterial({
      color: 0xc8e4f4,
      transparent: true,
      opacity: 0.65,
      side: THREE.DoubleSide,
      flatShading: true,
    });
    const wingShape = new THREE.Shape();
    wingShape.moveTo(0, 0);
    wingShape.lineTo(0.35, 0.35);
    wingShape.lineTo(1.35, 0.28);
    wingShape.lineTo(1.55, 0.06);
    wingShape.lineTo(0.55, -0.22);
    wingShape.lineTo(0, 0);
    const wingGeo = new THREE.ShapeGeometry(wingShape);

    const leftWingPivot = new THREE.Group();
    leftWingPivot.position.set(-0.18, 0.24, 0.05);
    fly.add(leftWingPivot);
    const leftWing = new THREE.Mesh(wingGeo, wingMat);
    leftWing.rotation.y = Math.PI - 0.2;
    leftWing.rotation.z = 0.25;
    leftWingPivot.add(leftWing);

    const rightWingPivot = new THREE.Group();
    rightWingPivot.position.set(0.18, 0.24, 0.05);
    fly.add(rightWingPivot);
    const rightWing = new THREE.Mesh(wingGeo, wingMat);
    rightWing.rotation.y = 0.2;
    rightWing.rotation.z = -0.25;
    rightWingPivot.add(rightWing);

    return {
      mesh: fly,
      leftWingPivot,
      rightWingPivot,
    };
  }

  // --- 6. 5v5 Fly Squads (10 Flies Total) on Enlarged Pitch (48 x 28) ---
  const teamRedFlies = [];
  const teamBlueFlies = [];
  const allFlies = [];

  // Formations scaled for 48 x 28
  const red5v5Formation = [
    { role: "GK", baseX: -22.2, baseZ: 0 },
    { role: "DEF1", baseX: -14.5, baseZ: -7.0 },
    { role: "DEF2", baseX: -14.5, baseZ: 7.0 },
    { role: "MID", baseX: -7.0, baseZ: 0 },
    { role: "ST", baseX: -2.2, baseZ: 0 },
  ];

  const blue5v5Formation = [
    { role: "GK", baseX: 22.2, baseZ: 0 },
    { role: "DEF1", baseX: 14.5, baseZ: -7.0 },
    { role: "DEF2", baseX: 14.5, baseZ: 7.0 },
    { role: "MID", baseX: 7.0, baseZ: 0 },
    { role: "ST", baseX: 2.2, baseZ: 0 },
  ];

  function setupTeam(formation, teamName, eyeColorHex, teamColorHex, teamList) {
    formation.forEach((slot, idx) => {
      const flyObj = createFlyModel(eyeColorHex, teamColorHex);
      flyObj.mesh.position.set(slot.baseX, 1.2, slot.baseZ);
      flyObj.mesh.rotation.y = teamName === "RED" ? Math.PI / 2 : -Math.PI / 2;
      scene.add(flyObj.mesh);

      const agent = {
        id: `${teamName}_${idx + 1}`,
        name: `${teamName === "RED" ? "Team Red" : "Team Blue"} #${idx + 1} ${slot.role}`,
        team: teamName,
        role: slot.role,
        mesh: flyObj.mesh,
        leftWingPivot: flyObj.leftWingPivot,
        rightWingPivot: flyObj.rightWingPivot,
        basePos: new THREE.Vector3(slot.baseX, 1.2, slot.baseZ),
        pos: flyObj.mesh.position,
        vel: new THREE.Vector3(),
        wingPhase: Math.random() * Math.PI * 2,
        kickCooldown: 0,
        stamina: 100.0,
        nervousLevel: 50.0,
      };

      teamList.push(agent);
      allFlies.push(agent);
    });
  }

  // Team Red: RED EYES (0xff0022), Red Collar
  setupTeam(red5v5Formation, "RED", 0xff0022, 0xff3344, teamRedFlies);
  // Team Blue: BLUE EYES (0x0088ff), Blue Collar
  setupTeam(blue5v5Formation, "BLUE", 0x0088ff, 0x0088ff, teamBlueFlies);

  // --- 7. Selection Ring & Interactive Fly Selection ---
  const selectRingGeo = new THREE.RingGeometry(0.7, 0.84, 32);
  const selectRingMat = new THREE.MeshBasicMaterial({
    color: 0xff3344,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.85,
  });
  const selectRing = new THREE.Mesh(selectRingGeo, selectRingMat);
  selectRing.rotation.x = -Math.PI / 2;
  selectRing.position.set(0, 0.02, 0);
  scene.add(selectRing);

  // --- 8. Match State & Biometric Telemetry UI Elements ---
  const match = {
    scoreRed: 0,
    scoreBlue: 0,
    seconds: 0,
    activePlayer: teamRedFlies[4],    // ST by default
    selectedPlayer: teamRedFlies[4],  // default chosen fly
    autoTrack: true,                  // if true, tracks closest fly to ball
    cameraMode: "tv",
    isGoalCelebration: false,
    goalScoredLocked: false,
  };

  const elScoreRed = document.getElementById("score-red");
  const elScoreBlue = document.getElementById("score-blue");
  const elClock = document.getElementById("match-time");
  const elGoalBanner = document.getElementById("goal-banner");
  const elGoalText = document.getElementById("goal-text");
  const elPlayerName = document.getElementById("active-player-name");

  // Biometric Elements (NO DOPAMINE)
  const elNervous = document.getElementById("val-nervous");
  const elNervousState = document.getElementById("val-nervous-state");
  const elNervousBar = document.getElementById("nervous-bar-fill");
  const elWingbeat = document.getElementById("val-wingbeat");
  const elWingbeatBar = document.getElementById("wingbeat-bar-fill");
  const elSpikes = document.getElementById("val-spikes");
  const elStamina = document.getElementById("val-stamina");
  const elOpticFlow = document.getElementById("val-optic-flow");
  const elDecision = document.getElementById("act-decision");
  const elPulseDot = document.getElementById("player-pulse-dot");
  const btnAutoTrack = document.getElementById("btn-auto-track");
  const btnMinimizeStats = document.getElementById("btn-minimize-stats");
  const neuralCard = document.getElementById("neural-card");

  if (btnMinimizeStats && neuralCard) {
    btnMinimizeStats.addEventListener("click", () => {
      const isMin = neuralCard.classList.toggle("minimized");
      btnMinimizeStats.innerHTML = isMin ? "&#43;" : "&#8722;";
      btnMinimizeStats.title = isMin ? "Expand Stats Window" : "Minimize Stats Window";
    });
  }

  // Reset all 10 flies cleanly back to base formation positions
  function resetAllFliesToFormation() {
    allFlies.forEach((fly) => {
      fly.pos.copy(fly.basePos);
      fly.vel.set(0, 0, 0);
      fly.mesh.rotation.y = fly.team === "RED" ? Math.PI / 2 : -Math.PI / 2;
      fly.mesh.rotation.z = 0;
      fly.mesh.rotation.x = 0;
      fly.kickCooldown = 0.8;
      fly.stamina = Math.min(100, fly.stamina + 20);
    });
  }

  // Waveform canvas
  const waveCanvas = document.getElementById("waveform-canvas");
  const wctx = waveCanvas.getContext("2d");
  const wavePoints = new Array(85).fill(21);

  function drawWaveform() {
    const w = waveCanvas.width;
    const h = waveCanvas.height;
    wctx.clearRect(0, 0, w, h);
    wctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
    wctx.lineWidth = 1;
    wctx.beginPath();
    wctx.moveTo(0, h / 2); wctx.lineTo(w, h / 2);
    wctx.stroke();

    const waveColor = match.activePlayer.team === "RED" ? "#ff4466" : "#00bbff";
    wctx.strokeStyle = waveColor;
    wctx.lineWidth = 1.8;
    wctx.shadowColor = waveColor;
    wctx.shadowBlur = 6;
    wctx.beginPath();
    for (let i = 0; i < wavePoints.length; i++) {
      const x = (i / (wavePoints.length - 1)) * w;
      const y = wavePoints[i];
      if (i === 0) wctx.moveTo(x, y);
      else wctx.lineTo(x, y);
    }
    wctx.stroke();
    wctx.shadowBlur = 0;
  }

  // Function to select a fly
  function selectFly(agent) {
    match.selectedPlayer = agent;
    match.activePlayer = agent;
    match.autoTrack = false;

    if (btnAutoTrack) {
      btnAutoTrack.classList.remove("active");
      btnAutoTrack.textContent = "MANUAL: CLICK TO AUTO";
    }

    // Update roster button highlights
    document.querySelectorAll(".fly-btn").forEach((b) => {
      b.classList.toggle("active", b.getAttribute("data-fly-id") === agent.id);
    });

    // Update selection ring color
    selectRingMat.color.setHex(agent.team === "RED" ? 0xff3344 : 0x0088ff);
  }

  // Roster buttons click handlers
  document.querySelectorAll(".fly-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const flyId = btn.getAttribute("data-fly-id");
      const targetFly = allFlies.find((f) => f.id === flyId);
      if (targetFly) selectFly(targetFly);
    });
  });

  if (btnAutoTrack) {
    btnAutoTrack.addEventListener("click", () => {
      match.autoTrack = true;
      btnAutoTrack.classList.add("active");
      btnAutoTrack.textContent = "AUTO: BALL TRACK";
    });
  }

  // 3D Raycaster: Click directly on any fly in the arena to select!
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();

  window.addEventListener("pointerdown", (event) => {
    if (event.target.closest(".top-scoreboard, .top-controls, .neural-activity-card, .roster-bar")) {
      return;
    }

    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);

    const hit = raycaster.intersectObjects(allFlies.map((f) => f.mesh), true);
    if (hit.length > 0) {
      let root = hit[0].object;
      while (root.parent && root.parent !== scene) {
        root = root.parent;
      }
      const chosen = allFlies.find((f) => f.mesh === root);
      if (chosen) selectFly(chosen);
    }
  });

  // Precision Goal Trigger with Strict Single Increment (+1) & Full Reset
  function triggerGoal(scoringTeam) {
    if (match.goalScoredLocked || match.isGoalCelebration) return;
    match.goalScoredLocked = true;
    match.isGoalCelebration = true;

    // 1. Freeze ball immediately and park safely in net
    ball.vel.set(0, 0, 0);
    const netX = scoringTeam === "RED" ? pitchHalfL + 1.2 : -pitchHalfL - 1.2;
    ball.pos.set(netX, ballRadius + 0.1, 0);

    // 2. Strict increment of exactly 1 goal
    if (scoringTeam === "RED") {
      match.scoreRed += 1;
      elScoreRed.textContent = match.scoreRed;
      elGoalText.innerHTML = "GOAL!<br><span style='font-size:36px; color:#ff3344; font-weight:800;'>TEAM RED SCORED</span>";
    } else {
      match.scoreBlue += 1;
      elScoreBlue.textContent = match.scoreBlue;
      elGoalText.innerHTML = "GOAL!<br><span style='font-size:36px; color:#0088ff; font-weight:800;'>TEAM BLUE SCORED</span>";
    }

    elGoalBanner.classList.add("show");

    // 3. Prevent kicking during celebration
    allFlies.forEach((fly) => {
      fly.kickCooldown = 2.8;
    });

    // 4. After 2.5 seconds: reset all flies and ball to center kick-off
    setTimeout(() => {
      resetAllFliesToFormation();
      resetBall(scoringTeam === "RED" ? "BLUE" : "RED");
      elGoalBanner.classList.remove("show");

      setTimeout(() => {
        match.isGoalCelebration = false;
        match.goalScoredLocked = false;
      }, 500);
    }, 2500);
  }

  // Camera buttons
  document.getElementById("btn-cam-tv").addEventListener("click", function () {
    document.querySelectorAll(".cam-btn").forEach((b) => b.classList.remove("active"));
    this.classList.add("active");
    match.cameraMode = "tv";
  });
  document.getElementById("btn-cam-ball").addEventListener("click", function () {
    document.querySelectorAll(".cam-btn").forEach((b) => b.classList.remove("active"));
    this.classList.add("active");
    match.cameraMode = "ball";
  });
  document.getElementById("btn-cam-fly").addEventListener("click", function () {
    document.querySelectorAll(".cam-btn").forEach((b) => b.classList.remove("active"));
    this.classList.add("active");
    match.cameraMode = "fly";
  });
  document.getElementById("btn-cam-tactical").addEventListener("click", function () {
    document.querySelectorAll(".cam-btn").forEach((b) => b.classList.remove("active"));
    this.classList.add("active");
    match.cameraMode = "tactical";
  });

  // Reset Match Button
  document.getElementById("btn-reset-ball").addEventListener("click", () => {
    match.scoreRed = 0;
    match.scoreBlue = 0;
    elScoreRed.textContent = 0;
    elScoreBlue.textContent = 0;
    match.seconds = 0;
    elClock.textContent = "00:00";
    match.isGoalCelebration = false;
    match.goalScoredLocked = false;
    elGoalBanner.classList.remove("show");
    resetAllFliesToFormation();
    resetBall("RED");
  });

  // --- 9. 60 FPS Physics & 5v5 Locomotive Engine ---
  let lastTime = performance.now();
  let clockTimer = 0;

  function animate(now) {
    requestAnimationFrame(animate);
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    lastTime = now;

    // Match clock
    if (!match.isGoalCelebration) {
      clockTimer += dt;
      if (clockTimer >= 1.0) {
        match.seconds++;
        clockTimer = 0;
        const mins = Math.floor(match.seconds / 60).toString().padStart(2, "0");
        const secs = (match.seconds % 60).toString().padStart(2, "0");
        elClock.textContent = `${mins}:${secs}`;
      }
    }

    // --- Ball Physics ---
    if (!match.isGoalCelebration) {
      ball.vel.y -= 9.8 * dt; // Gravity
      ball.pos.addScaledVector(ball.vel, dt);

      // Turf bounce
      if (ball.pos.y <= ball.radius) {
        ball.pos.y = ball.radius;
        ball.vel.y = -ball.vel.y * 0.65;
        ball.vel.x *= 0.985;
        ball.vel.z *= 0.985;
      }

      // Sideline bounce
      if (Math.abs(ball.pos.z) > pitchHalfW - ball.radius) {
        ball.pos.z = Math.sign(ball.pos.z) * (pitchHalfW - ball.radius);
        ball.vel.z = -ball.vel.z * 0.7;
      }

      // Goal & Endline Check
      if (Math.abs(ball.pos.x) > pitchHalfL) {
        if (Math.abs(ball.pos.z) < goalWidth / 2 && ball.pos.y < goalHeight) {
          // Strict Single Goal Trigger
          if (ball.pos.x > pitchHalfL) triggerGoal("RED");
          else triggerGoal("BLUE");
        } else {
          // Rebound from endline outside goal
          ball.pos.x = Math.sign(ball.pos.x) * pitchHalfL;
          ball.vel.x = -ball.vel.x * 0.7;
        }
      }
    }

    ballMesh.position.copy(ball.pos);
    ballMesh.rotation.x += ball.vel.z * dt * 2.5;
    ballMesh.rotation.z -= ball.vel.x * dt * 2.5;

    // --- Closest Fly to Ball on Each Team ---
    let closestRed = teamRedFlies[0];
    let minDistRed = 999;
    teamRedFlies.forEach((f) => {
      const d = f.pos.distanceTo(ball.pos);
      if (d < minDistRed) { minDistRed = d; closestRed = f; }
    });

    let closestBlue = teamBlueFlies[0];
    let minDistBlue = 999;
    teamBlueFlies.forEach((f) => {
      const d = f.pos.distanceTo(ball.pos);
      if (d < minDistBlue) { minDistBlue = d; closestBlue = f; }
    });

    // Determine Active Player (Auto-track closest or Manual Selection)
    if (match.autoTrack) {
      match.activePlayer = minDistRed <= minDistBlue ? closestRed : closestBlue;
      // Update UI roster button for auto tracking
      document.querySelectorAll(".fly-btn").forEach((b) => {
        b.classList.toggle("active", b.getAttribute("data-fly-id") === match.activePlayer.id);
      });
      selectRingMat.color.setHex(match.activePlayer.team === "RED" ? 0xff3344 : 0x0088ff);
    } else {
      match.activePlayer = match.selectedPlayer;
    }

    // Update Selection Ring Position & Pulse
    selectRing.position.set(match.activePlayer.pos.x, 0.02, match.activePlayer.pos.z);
    selectRing.rotation.z += dt * 1.5;

    // --- 5v5 Fly Locomotive & Tactical AI ---
    allFlies.forEach((fly) => {
      if (fly.kickCooldown > 0) fly.kickCooldown -= dt;

      // If goal celebration: return flies smoothly to formation positions
      if (match.isGoalCelebration) {
        fly.pos.lerp(fly.basePos, dt * 4.5);
        fly.vel.set(0, 0, 0);
        const homeFacing = fly.team === "RED" ? Math.PI / 2 : -Math.PI / 2;
        fly.mesh.rotation.y = THREE.MathUtils.lerp(fly.mesh.rotation.y, homeFacing, dt * 6.0);
        fly.mesh.rotation.x = 0;
        fly.mesh.rotation.z = 0;

        fly.wingPhase += dt * 70;
        const flap = Math.sin(fly.wingPhase) * 0.35;
        fly.leftWingPivot.rotation.z = 0.25 + flap;
        fly.rightWingPivot.rotation.z = -0.25 - flap;
        return;
      }

      const isClosest = (fly === closestRed || fly === closestBlue);
      const targetPos = new THREE.Vector3();

      if (fly.role === "GK") {
        // Goalkeeper lateral patrol along the goal line
        targetPos.copy(fly.basePos);
        targetPos.z = THREE.MathUtils.clamp(ball.pos.z * 0.8, -goalWidth / 2 + 0.5, goalWidth / 2 - 0.5);
        targetPos.y = 0.85 + Math.sin(now * 0.005 + fly.basePos.x) * 0.25;

        // Diving save only when ball is inside the D area, remaining anchored to the goal mouth
        const distFromGoal = Math.abs(fly.basePos.x - ball.pos.x);
        if (distFromGoal < 4.5 && Math.abs(ball.pos.z) < goalWidth / 2 + 1.2) {
          targetPos.copy(ball.pos);
          const maxAdvance = 2.0;
          targetPos.x = THREE.MathUtils.clamp(
            ball.pos.x,
            fly.team === "RED" ? fly.basePos.x : fly.basePos.x - maxAdvance,
            fly.team === "RED" ? fly.basePos.x + maxAdvance : fly.basePos.x
          );
          targetPos.z = THREE.MathUtils.clamp(ball.pos.z, -goalWidth / 2 + 0.2, goalWidth / 2 - 0.2);
        }
      } else if (isClosest) {
        // Attack/Striker Mode: Full sprint diving at ball
        targetPos.copy(ball.pos);
        targetPos.y = Math.max(0.42, ball.pos.y + 0.12);
        fly.stamina = Math.max(25, fly.stamina - dt * 2.8);
      } else {
        // Dynamic Zone Coverage
        const shiftX = (ball.pos.x - fly.basePos.x) * 0.42;
        const shiftZ = (ball.pos.z - fly.basePos.z) * 0.42;
        targetPos.set(
          fly.basePos.x + shiftX,
          1.15 + Math.sin(now * 0.004 + fly.pos.x) * 0.2,
          fly.basePos.z + shiftZ
        );
        fly.stamina = Math.min(100, fly.stamina + dt * 1.6);
      }

      // Steering Vector
      const steer = new THREE.Vector3().subVectors(targetPos, fly.pos);
      const dist = steer.length();
      steer.normalize();

      const speed = isClosest ? 9.6 : 6.0;
      fly.vel.lerp(steer.multiplyScalar(speed), dt * 4.5);
      fly.pos.addScaledVector(fly.vel, dt);

      // Orientation & LookAt
      if (dist > 0.1) {
        const lookTarget = isClosest
          ? (fly.team === "RED" ? new THREE.Vector3(pitchHalfL, 0.5, 0) : new THREE.Vector3(-pitchHalfL, 0.5, 0))
          : targetPos;
        const angleY = Math.atan2(lookTarget.x - fly.pos.x, lookTarget.z - fly.pos.z);
        fly.mesh.rotation.y = THREE.MathUtils.lerp(fly.mesh.rotation.y, angleY, dt * 8.0);
      }

      // Dynamic Banking
      fly.mesh.rotation.z = -fly.vel.x * 0.04;
      fly.mesh.rotation.x = fly.vel.z * 0.04;

      // High-Frequency Wingbeats
      fly.wingPhase += dt * (isClosest ? 135 : 85);
      const flap = Math.sin(fly.wingPhase) * 0.45;
      fly.leftWingPivot.rotation.z = 0.25 + flap;
      fly.rightWingPivot.rotation.z = -0.25 - flap;

      // Ball Kick / Strike
      const ballDist = fly.pos.distanceTo(ball.pos);
      if (ballDist < 0.85 && fly.kickCooldown <= 0 && !match.isGoalCelebration) {
        fly.kickCooldown = 0.35;
        const targetGoalX = fly.team === "RED" ? pitchHalfL : -pitchHalfL;
        const kickDir = new THREE.Vector3(
          targetGoalX - ball.pos.x,
          Math.random() * 2.2 + 1.2,
          (Math.random() - 0.5) * 4.0 - ball.pos.z * 0.5
        ).normalize();

        const power = Math.random() * 6.5 + 11.0;
        ball.vel.copy(kickDir.multiplyScalar(power));

        if (fly === match.activePlayer) {
          elDecision.textContent = "STRIKING BALL!";
        }
      }
    });

    // --- 10. Real-time Biometrics for Active / Selected Fly ---
    const active = match.activePlayer;
    const isActClosest = (active === closestRed || active === closestBlue);
    const dBall = active.pos.distanceTo(ball.pos);

    // Dynamic Nervous / Arousal Level
    const nervous = Math.round(
      THREE.MathUtils.clamp(
        100 - dBall * 4.0 + (isActClosest ? 22 : 0) + (active.role === "GK" && Math.abs(ball.pos.x - active.basePos.x) < 8 ? 30 : 0),
        18,
        98
      )
    );
    active.nervousLevel = THREE.MathUtils.lerp(active.nervousLevel, nervous, dt * 5.0);
    const curNervous = Math.round(active.nervousLevel);

    elPlayerName.textContent = active.name;
    elPlayerName.style.color = active.team === "RED" ? "#ff3344" : "#0088ff";

    elNervous.textContent = curNervous;
    elNervousBar.style.width = curNervous + "%";

    if (curNervous >= 85) {
      elNervousState.textContent = "MAX ADRENALINE SPIKE";
      elNervousState.style.color = "#ff3344";
      elPulseDot.style.background = "#ff3344";
      elPulseDot.style.boxShadow = "0 0 10px #ff3344";
    } else if (curNervous >= 65) {
      elNervousState.textContent = "HIGH ALERT (DANGER ZONE)";
      elNervousState.style.color = "#d8ff00";
      elPulseDot.style.background = "#d8ff00";
      elPulseDot.style.boxShadow = "0 0 10px #d8ff00";
    } else if (curNervous >= 45) {
      elNervousState.textContent = "FOCUSED ENGAGEMENT";
      elNervousState.style.color = "#00d8ff";
      elPulseDot.style.background = "#00d8ff";
      elPulseDot.style.boxShadow = "0 0 10px #00d8ff";
    } else {
      elNervousState.textContent = "CALM PATROL";
      elNervousState.style.color = "#00ff88";
      elPulseDot.style.background = "#00ff88";
      elPulseDot.style.boxShadow = "0 0 10px #00ff88";
    }

    // Wingbeat Frequency
    const wingHz = Math.round(isActClosest ? 195 + Math.sin(now * 0.01) * 15 : 148 + Math.sin(now * 0.008) * 10);
    elWingbeat.textContent = wingHz;
    elWingbeatBar.style.width = Math.min(100, Math.round((wingHz / 220) * 100)) + "%";

    // Spikes (Scaled to nervous level & motor drive)
    const spikes = Math.round(curNervous * 580 + (isActClosest ? 14000 : 4000) + Math.sin(now * 0.02) * 1800);
    elSpikes.textContent = spikes.toLocaleString();

    // Stamina
    elStamina.textContent = Math.round(active.stamina);

    // Optic Flow relative angle
    const toBall = new THREE.Vector2(ball.pos.x - active.pos.x, ball.pos.z - active.pos.z).normalize();
    const forwardVec = new THREE.Vector2(0, 1).rotateAround(new THREE.Vector2(0, 0), -active.mesh.rotation.y);
    const dot = forwardVec.dot(toBall);
    const cross = forwardVec.x * toBall.y - forwardVec.y * toBall.x;

    if (dot > 0.85) {
      elOpticFlow.textContent = "Optic: Target Direct Ahead";
    } else if (cross > 0.1) {
      elOpticFlow.textContent = `Optic: Approaching Right (${Math.round(Math.acos(THREE.MathUtils.clamp(dot, -1, 1)) * 57.3)}°)`;
    } else {
      elOpticFlow.textContent = `Optic: Approaching Left (${Math.round(Math.acos(THREE.MathUtils.clamp(dot, -1, 1)) * 57.3)}°)`;
    }

    // Tactical Intent
    if (active.kickCooldown > 0) {
      elDecision.textContent = "STRIKING BALL!";
    } else if (isActClosest) {
      elDecision.textContent = active.team === "RED" ? "ATTACKING BLUE GOAL" : "ATTACKING RED GOAL";
    } else if (active.role === "GK") {
      elDecision.textContent = Math.abs(ball.pos.x - active.basePos.x) < 5.0 ? "GOALKEEPER DIVING BLOCK" : "GUARDING GOAL LINE";
    } else if (active.role.startsWith("DEF")) {
      elDecision.textContent = "MARKING OFFENSIVE ZONE";
    } else {
      elDecision.textContent = "MIDFIELD TRANSITION & PASS";
    }

    // --- 11. Camera Positioning ---
    if (match.cameraMode === "tv") {
      const camTargetX = THREE.MathUtils.clamp(ball.pos.x * 0.55, -pitchHalfL + 9, pitchHalfL - 9);
      camera.position.lerp(new THREE.Vector3(camTargetX, 22, 32), dt * 3.2);
      controls.target.lerp(new THREE.Vector3(camTargetX, 0.8, 0), dt * 3.2);
    } else if (match.cameraMode === "ball") {
      camera.position.lerp(new THREE.Vector3(ball.pos.x - 7, ball.pos.y + 4.5, ball.pos.z + 9), dt * 4.0);
      controls.target.lerp(ball.pos, dt * 6.0);
    } else if (match.cameraMode === "fly") {
      const f = match.activePlayer;
      const forward = new THREE.Vector3(0, 0, 1).applyAxisAngle(new THREE.Vector3(0, 1, 0), f.mesh.rotation.y);
      const camPos = f.pos.clone().add(new THREE.Vector3(0, 0.45, 0)).sub(forward.clone().multiplyScalar(1.5));
      camera.position.lerp(camPos, dt * 8.0);
      controls.target.lerp(f.pos.clone().add(forward.clone().multiplyScalar(5.0)), dt * 8.0);
    } else if (match.cameraMode === "tactical") {
      camera.position.lerp(new THREE.Vector3(0, 52, 0.1), dt * 3.0);
      controls.target.lerp(new THREE.Vector3(0, 0, 0), dt * 3.0);
    }
    controls.update();

    // Waveform Update
    wavePoints.shift();
    const waveAmp = THREE.MathUtils.clamp((curNervous / 100) * 26, 6, 26);
    const noise = (Math.random() - 0.5) * waveAmp;
    wavePoints.push(21 + noise);
    drawWaveform();

    renderer.render(scene, camera);
  }

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  requestAnimationFrame(animate);
})();

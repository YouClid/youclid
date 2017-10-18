
let scene, camera, raycaster, renderer, objects, mouse, geometry

let size = Math.min(window.innerWidth*0.65, window.innerHeight)

let current = null
let oldPos = null
let newPos = null
let originalCenter = null


function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera( 75, 1, 1, 1000 );
    camera.position.set(0, 0, 20 );
    // camera.lookAt(new THREE.Vector3(0, 0, 0));

    raycaster = new THREE.Raycaster();

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(size, size);
    document.body.appendChild( renderer.domElement );

    renderer.render(scene, camera)

    mouse = new THREE.Vector2();

    objects = []

    loadGeometry(scene, camera)

    // document.addEventListener( 'mousedown', onMouseDown, false );
    // document.addEventListener( 'mousemove', onMouseMove, false );
    // document.addEventListener( 'mouseup', onMouseUp, false );
    // document.addEventListener( 'touchstart', onTouchStart, false );
    // document.addEventListener( 'touchmove', onTouchMove, false );
    // document.addEventListener( 'touchend', onTouchEnd, false );
    window.onresize = resize;
    animate();
}

function animate() {
    requestAnimationFrame( animate );
    renderer.render( scene, camera );
    
}

function resize() {
    size = Math.min(window.innerWidth*0.65, window.innerHeight)
    renderer.setSize(size, size)
}


function loadGeometry(scene, camera) {

    geo = geometry.geometry

    let points = geo.filter(entry => entry.type === "Point")

    let pointMap = {}
    for(let i = 0; i < points.length; i++) {
	let point = points[i]
	pointMap[point.id] = point.data
	let p = makePoint(point.data)
	// pointMap[point.id] = p.geometry.vertices[0]
	objects.push(p)
	scene.add(p)
    }

    let circles = geo.filter(entry => entry.type === "Circle")

    for(let i = 0; i < circles.length; i++) {
	let circle = circles[i]

	let d = circle.data

	let c = makeCircle(pointMap[d.p1], pointMap[d.p2], pointMap[d.p3])
	objects.push(c)
	scene.add(c)
    }

    let lines = geo.filter(entry => entry.type === "Line")

    for(let i = 0; i< lines.length; i++) {
	let line = lines[i]
	let d = line.data

	let l = makeLine(pointMap[d.p1], pointMap[d.p2], true)

	objects.push(l)
	scene.add(l)
    }

    
}

function dist(p1, p2) {
    if(p1.z && p2.z) {
	let xs, ys, zs
	xs = (p1.x-p2.x)*(p1.x-p2.x)
	ys = (p1.y-p2.y)*(p1.y-p2.y)
	zs = (p1.z-p2.z)*(p1.z-p2.z)
	return Math.sqrt(xs+ys+zs)
    } else {
	return Math.sqrt((p1.x-p2.x)*(p1.x-p2.x)+(p1.y-p2.y)*(p1.y-p2.y))
    }
}

function makeLine(p1, p2, isNDC) {
    let wp1, wp2
    if(isNDC) {
	wp1 = NDCtoWorld(p1.x, p1.y, camera)
	wp2 = NDCtoWorld(p2.x, p2.y, camera)
    } else {
	wp1 = p1, wp2 = p2
    }

    let g = new THREE.Geometry()
    g.vertices.push(wp1, wp2)
    let m = new THREE.MeshBasicMaterial( { color: 0x990000 } )

    return new THREE.Line(g,m)
}

function checkCircle(p1, p2, p3, c) {
    let m1 = (p1.y-p2.y)/(p1.x-p2.x)
    let m2 = (p3.y-p2.y)/(p3.x-p2.x)

    let ma = -1.0*(1.0/m1)
    let mb = -1.0*(1.0/m2)

    let xa = 0.5*(p1.x+p2.x)
    let ya = 0.5*(p1.y+p2.y)
    let xb = 0.5*(p2.x+p3.x)
    let yb = 0.5*(p2.y+p3.y)

    let center = new THREE.Vector3()

    center.x = ((ma*xa)-(mb*xb)+yb-ya)/(ma-mb)
    center.y = (mb*(center.x-xb))+yb

    console.log(center)
    console.log(c)
    console.log(center.x == c.x && center.y == c.y)
}

function makeCircle(p1, p2, p3, isWorld) {
    if(!isWorld) {
	p1 = NDCtoWorld(p1.x, p1.y, camera)
	p2 = NDCtoWorld(p2.x, p2.y, camera)
	p3 = NDCtoWorld(p3.x, p3.y, camera)
    }
    let m1 = (p1.y-p2.y)/(p1.x-p2.x)
    let m2 = (p3.y-p2.y)/(p3.x-p2.x)

    let ma = -1.0*(1.0/m1)
    let mb = -1.0*(1.0/m2)

    let xa = 0.5*(p1.x+p2.x)
    let ya = 0.5*(p1.y+p2.y)
    let xb = 0.5*(p2.x+p3.x)
    let yb = 0.5*(p2.y+p3.y)

    let center = new THREE.Vector3()

    center.x = ((ma*xa)-(mb*xb)+yb-ya)/(ma-mb)
    center.y = (mb*(center.x-xb))+yb
    center.z = 0

    let worldCenter, worldPoint

    
    worldCenter = center
    worldPoint = p1
    // worldCenter = NDCtoWorld(center.x, center.y, camera)
    // worldPoint  = NDCtoWorld(p1.x, p1.y, camera)
    

    let radius = dist(worldCenter, worldPoint)

    let circleMaterial = new THREE.MeshBasicMaterial( { color: 0x009900 } );
    let circleGeom = new THREE.CircleGeometry(radius, 100);
    circleGeom.vertices.shift()
    circleGeom.vertices.push(circleGeom.vertices[0])
    var circle = new THREE.Line( circleGeom, circleMaterial );
    circle.position.set(worldCenter.x, worldCenter.y, worldCenter.z)

    return circle
    
    
}


// NDC stands for normalized device coordinates
function NDCtoWorld(x, y, camera) {
    let ndcVec = new THREE.Vector2(x, y)
    let plane = new THREE.Plane(new THREE.Vector3(0,0,1))
    let raycaster = new THREE.Raycaster()
    raycaster.setFromCamera( ndcVec, camera )
    let pos = raycaster.ray.intersectPlane(plane)
    return pos
}


function makePoint(point) {
    // Point has an x and a y attribute in NDC coordinates
    let PARTICLE_SIZE = 0.5

    let vertex = NDCtoWorld(point.x, point.y, camera)

    let geometry = new THREE.Geometry();
    geometry.vertices.push(vertex)
    let material = new THREE.PointsMaterial( { size: PARTICLE_SIZE, color: 0x888888 } )

    let particle = new THREE.Points( geometry, material );
    particle.material.depthTest = false
    particle.renderOrder = 1000
    return particle
}



/*
  All Event Callbacks
*/

function onMouseDown( event ) {
    event.preventDefault();
    mouse.x = ( event.clientX / size ) * 2 - 1;
    mouse.y = - ( event.clientY / size ) * 2 + 1;
    raycaster.setFromCamera( mouse, camera );
    let intersects = raycaster.intersectObjects( objects );
    if ( intersects.length > 0 ) {
	current = intersects[0]
	oldPos = current.point.clone()
	originalCenter = current.object.position.clone()
	// originalCenter = current.object.geometry.vertices[0].clone()
    }
}

function onMouseMove( event ) {
    event.preventDefault();
    if ( current ) {
	mouse.x = ( event.clientX / size ) * 2 - 1;
	mouse.y = - ( event.clientY / size ) * 2 + 1;
	let pos = NDCtoWorld(mouse.x, mouse.y, camera)
	newPos = pos.sub(oldPos)
	newPos.add(originalCenter)
	current.object.position.set(newPos.x, newPos.y, newPos.z)
	// let v = current.object.geometry.vertices[0]
	// v.x = newPos.x
	// v.y = newPos.y
	// v.z = newPos.z
	// current.object.geometry.verticesNeedUpdate = true
    } 
}

function onMouseUp( event ) {
    current = null;
}

function onTouchStart( event ) {
    event.preventDefault();
    event.clientX = event.touches[0].clientX;
    event.clientY = event.touches[0].clientY;
    onMouseDown( event );
}

function onTouchMove( event ) {
    event.preventDefault();
    event.clientX = event.touches[0].clientX;
    event.clientY = event.touches[0].clientY;
    onMouseMove( event );
}

function onTouchEnd( event ) {
    event.preventDefault();
    onMouseUp( event );
}



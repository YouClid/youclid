
let scene, camera, raycaster, renderer, objects, mouse, geometry

let current = null
let oldPos = null
let newPos = null
let originalCenter = null

//window.onload = init


function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 1, 1000 );
    camera.position.set(0, 0, 20 );
    // camera.lookAt(new THREE.Vector3(0, 0, 0));

    raycaster = new THREE.Raycaster();

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize( window.innerWidth, window.innerHeight);
    document.body.appendChild( renderer.domElement );

    renderer.render(scene, camera)

    mouse = new THREE.Vector2();


    var material = new THREE.LineBasicMaterial({ color: 0xffff00 });

    var geometry = new THREE.Geometry();
    geometry.vertices.push(new THREE.Vector3(-10, 0, 0));
    geometry.vertices.push(new THREE.Vector3(0, 10, 0));
    geometry.vertices.push(new THREE.Vector3(10, 0, 0));
    geometry.vertices.push(new THREE.Vector3(0, -10, 0));
    geometry.vertices.push(new THREE.Vector3(-10, 0, 0));
    
    var line = new THREE.Line(geometry, material);

    let circleMaterial = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
    let circleGeom = new THREE.CircleGeometry(3, 100);
    var circle = new THREE.Mesh( circleGeom, circleMaterial );


    objects = []
    // objects.push(line)
    // objects.push(circle)

    // scene.add(line);
    // scene.add(circle);

    loadGeometry(scene, camera)

    document.addEventListener( 'mousedown', onMouseDown, false );
    document.addEventListener( 'mousemove', onMouseMove, false );
    document.addEventListener( 'mouseup', onMouseUp, false );
    document.addEventListener( 'touchstart', onTouchStart, false );
    document.addEventListener( 'touchmove', onTouchMove, false );
    document.addEventListener( 'touchend', onTouchEnd, false );

    animate();
}

function animate() {
    requestAnimationFrame( animate );
    renderer.render( scene, camera );
    
}


function loadGeometry(scene, camera) {

    geo = geometry.geometry

    points = geo.filter(entry => entry.type === "Point")

    pointMap = {}
    for(let i = 0; i < points.length; i++) {
	let point = points[i]
	pointMap[point.id] = point.data
	let p = makePoint(point.data)
	objects.push(p)
	scene.add(p)
    }

    circles = geo.filter(entry => entry.type === "Circle")

    for(let i = 0; i < circles.length; i++) {
	let circle = circles[i]

	let d = circle.data
	
	let c = makeCircle(pointMap[d.p1], pointMap[d.p2], pointMap[d.p3])
	objects.push(c)
	scene.add(c)
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

function makeCircle(p1, p2, p3) {
    let ma = -(p2.x-p1.x)/(p2.y-p1.y)
    let mb = -(p3.x-p2.x)/(p3.y-p2.y)
    let xa = 0.5*(p1.x+p2.x)
    let ya = 0.5*(p1.y+p2.y)
    let xb = 0.5*(p2.x+p3.x)
    let yb = 0.5*(p2.y+p3.y)

    let center = {}

    center.x = ((ma*xa)-(mb*xb)+yb-ya)/(ma-mb)
    center.y = (ma*(center.x-xa))+ya

    let worldCenter = NDCtoWorld(center.x, center.y, camera)
    let worldPoint  = NDCtoWorld(p1.x, p1.y, camera)

    let radius = dist(worldCenter, worldPoint)

    let circleMaterial = new THREE.MeshBasicMaterial( { color: 0xffffff } );
    let circleGeom = new THREE.CircleGeometry(radius, 100);
    var circle = new THREE.Mesh( circleGeom, circleMaterial );
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

function addPoints(points) {
    // points should be an array of objects
    // each with an x and a y attribute in NDC coordinate
    let PARTICLE_SIZE = 0.5

    let vertices = points.map(p => NDCtoWorld(p.x, p.y, camera))

    let positions = new Float32Array( vertices.length * 3 );
    let colors = new Float32Array( vertices.length * 3 );
    let sizes = new Float32Array( vertices.length );
    let vertex;
    let color = new THREE.Color();
    for ( let i = 0, l = vertices.length; i < l; i ++ ) {
	vertex = vertices[ i ];
	vertex.toArray( positions, i * 3 );
	color.setHSL( 0.01 + 0.1 * ( i / l ), 1.0, 0.5 );
	color.toArray( colors, i * 3 );
	sizes[ i ] = PARTICLE_SIZE * 0.5;
    }
    let geometry = new THREE.BufferGeometry();
    geometry.addAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );
    geometry.addAttribute( 'customColor', new THREE.BufferAttribute( colors, 3 ) );
    geometry.addAttribute( 'size', new THREE.BufferAttribute( sizes, 1 ) );
    //
    let material = new THREE.PointsMaterial( { size: PARTICLE_SIZE, color: 0x888888 } )
    //
    let particles = new THREE.Points( geometry, material );
    return particles
}

function makePoint(point) {
    // points should be an array of objects
    // each with an x and a y attribute in NDC coordinate
    let PARTICLE_SIZE = 0.5

    let vertices = [NDCtoWorld(point.x, point.y, camera)]

    let positions = new Float32Array( vertices.length * 3 );
    let colors = new Float32Array( vertices.length * 3 );
    let sizes = new Float32Array( vertices.length );
    let vertex;
    let color = new THREE.Color();
    for ( let i = 0, l = vertices.length; i < l; i ++ ) {
	vertex = vertices[ i ];
	vertex.toArray( positions, i * 3 );
	color.setHSL( 0.01 + 0.1 * ( i / l ), 1.0, 0.5 );
	color.toArray( colors, i * 3 );
	sizes[ i ] = PARTICLE_SIZE * 0.5;
    }
    let geometry = new THREE.BufferGeometry();
    geometry.addAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );
    geometry.addAttribute( 'customColor', new THREE.BufferAttribute( colors, 3 ) );
    geometry.addAttribute( 'size', new THREE.BufferAttribute( sizes, 1 ) );
    //
    let material = new THREE.PointsMaterial( { size: PARTICLE_SIZE, color: 0x888888 } )
    //
    let particle = new THREE.Points( geometry, material );
    return particle
}



/*
  All Event Callbacks
*/

function onMouseDown( event ) {
    event.preventDefault();
    mouse.x = ( event.clientX / renderer.domElement.clientWidth ) * 2 - 1;
    mouse.y = - ( event.clientY / renderer.domElement.clientHeight ) * 2 + 1;
    raycaster.setFromCamera( mouse, camera );
    let intersects = raycaster.intersectObjects( objects );
    if ( intersects.length > 0 ) {
	current = intersects[0]
	oldPos = current.point.clone()
	originalCenter = current.object.position.clone()
    }
}

function onMouseMove( event ) {
    event.preventDefault();
    if ( current ) {
	mouse.x = ( event.clientX / renderer.domElement.clientWidth ) * 2 - 1;
	mouse.y = - ( event.clientY / renderer.domElement.clientHeight ) * 2 + 1;
	let pos = NDCtoWorld(mouse.x, mouse.y, camera)
	newPos = pos.sub(oldPos)
	newPos.add(originalCenter)
	current.object.position.set(newPos.x, newPos.y, newPos.z)
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



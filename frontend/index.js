

var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 1, 1000 );
camera.position.set(0, 0, 20 );
// camera.lookAt(new THREE.Vector3(0, 0, 0));

let raycaster = new THREE.Raycaster();

var renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );


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

let mouse = new THREE.Vector2();

let objects = []
objects.push(line)
objects.push(circle)

scene.add(line);
scene.add(circle);

function animate() {
    requestAnimationFrame( animate );
    renderer.render( scene, camera );
    
}

let current = null
let plane = new THREE.Plane(new THREE.Vector3(0,0,1))
let oldPos = null
let newPos = null
let originalCenter = null

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
	raycaster.setFromCamera( mouse, camera );
	let pos = raycaster.ray.intersectPlane(plane)
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


    
animate();
document.addEventListener( 'mousedown', onMouseDown, false );
document.addEventListener( 'mousemove', onMouseMove, false );
document.addEventListener( 'mouseup', onMouseUp, false );
document.addEventListener( 'touchstart', onTouchStart, false );
document.addEventListener( 'touchmove', onTouchMove, false );
document.addEventListener( 'touchend', onTouchEnd, false );

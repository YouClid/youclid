
let scene, camera, raycaster, renderer, mouse, geometry, scenes, anim_index, canvasRect

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

    canvasRect = renderer.domElement.getBoundingClientRect()
    
    renderer.render(scene, camera)

    mouse = new THREE.Vector2();

    anim_index = 0
    scenes = loadGeometry(camera)

    // document.addEventListener( 'mousedown', onMouseDown, false );
    document.addEventListener( 'mousemove', onMouseMove, false );
    // document.addEventListener( 'mouseup', onMouseUp, false );
    // document.addEventListener( 'touchstart', onTouchStart, false );
    // document.addEventListener( 'touchmove', onTouchMove, false );
    // document.addEventListener( 'touchend', onTouchEnd, false );
    document.addEventListener( 'keydown', onKeyDown)

/*Adds listeners for hovering over text span elements */
    var mydiv = document.getElementById("text");
    mydiv.addEventListener("mouseover", overTextChange, false);
    mydiv.addEventListener("mouseout", overTextRevert, false);

    window.onresize = resize;
    animate();
}

function animate() {
    scene = scenes[anim_index];
    requestAnimationFrame( animate );
    renderer.render( scene, camera );

}

function resize() {
    size = Math.min(window.innerWidth*0.65, window.innerHeight)
    renderer.setSize(size, size)
    canvasRect = renderer.domElement.getBoundingClientRect()
}


function loadGeometry(camera) {
    let scenes = []

    let steps = geometry.animations.map(arr => arr.map(obj => geometry.geometry[obj]))

    let temp = new THREE.Scene()
    for(let i = 0; i < steps.length; i++) {
	let geo = steps[i]
	scene = temp.clone()

	let points = geo.filter(entry => entry.type === "Point")

	let pointMap = {}
	for(let i = 0; i < points.length; i++) {
	    let point = points[i]
	    pointMap[point.id] = point.data
	    let p = makePoint(point.id, point.data)
	    // pointMap[point.id] = p.geometry.vertices[0]
	    scene.add(p)
	}

	let circles = geo.filter(entry => entry.type === "Circle")

	for(let i = 0; i < circles.length; i++) {
	    let circle = circles[i]

	    let d = circle.data

	    let c = makeCircle(circle.id, pointMap[d.p1], pointMap[d.p2], pointMap[d.p3])
	    scene.add(c)
	}

	let lines = geo.filter(entry => entry.type === "Line")

	for(let i = 0; i< lines.length; i++) {
	    let line = lines[i]
	    let d = line.data

	    let l = makeLine(line.id, pointMap[d.p1], pointMap[d.p2], true)

	    scene.add(l)
	}
	scenes.push(scene)
    }

    return scenes
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

function makeLine(ident, p1, p2, isNDC) {
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

    let lineret  = new THREE.Line(g,m)
    let namestart = "object_line_";
    lineret.name = namestart.concat(ident.toString());
    return lineret;
}

function makeCircle(ident, p1, p2, p3, isWorld) {
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

    let namestart = "object_circle_";
    circle.name = namestart.concat(ident.toString());

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


function makePoint(ident, point) {
    // Point has an x and a y attribute in NDC coordinates
    let PARTICLE_SIZE = 0.5

    let vertex = NDCtoWorld(point.x, point.y, camera)

    let geometry = new THREE.Geometry();
    geometry.vertices.push(vertex)
    let material = new THREE.PointsMaterial( { size: PARTICLE_SIZE, color: 0x888888 } )

    let particle = new THREE.Points( geometry, material );
    particle.material.depthTest = false
    particle.renderOrder = 1000

    let namestart = "object_point_";
    particle.name = namestart.concat(ident.toString());

    return particle
}



/*
  All Event Callbacks
*/

/* Two functions for hovering over span elements, and leaving from hover */
function overTextChange(event)  {
    if(event.target.tagName === "SPAN") {
        event.target.style.backgroundColor = "yellow";
        let obj_id_str = event.target.id.replace('text', 'object');
        //alert(obj_id_str);
        testname = scene.getObjectByName(obj_id_str);
        //alert(testname.name);
        if(testname != null){
          oldcolor = new THREE.Color( testname.material.color );
          testname.material.color.setHex( 0xfffa00 );
      }
    }
}

function overTextRevert(event)  {
    if(event.target.tagName === "SPAN") {
        event.target.style.backgroundColor = "#dddddd";
        if(testname != null){
          testname.material.color.setHex( oldcolor.getHex() );
      }
        oldcolor=null;
        testname=null;
   }
}


function onMouseDown( event ) {
    event.preventDefault();
    mouse.x = ( event.clientX / size ) * 2 - 1;
    mouse.y = - ( event.clientY / size ) * 2 + 1;
    raycaster.setFromCamera( mouse, camera );
    let intersects = raycaster.intersectObjects(scene.children);
    if ( intersects.length > 0 ) {
	current = intersects[0]
	oldPos = current.point.clone()
	originalCenter = current.object.position.clone()
	// originalCenter = current.object.geometry.vertices[0].clone()
    }
}

let changed = {text:[], objects:[]}
let objectColors = {}

function onMouseMove( event ) {
    let xgood = event.clientX > canvasRect.left && event.clientX < canvasRect.right
    let ygood = event.clientY > canvasRect.top  && event.clientY < canvasRect.bottom
    let text = []
    let objects = []

    if(xgood && ygood) {
	mouse.x = ((event.clientX - canvasRect.left) / size ) * 2 - 1;
	mouse.y = - ( (event.clientY - canvasRect.top) / size ) * 2 + 1;
	raycaster.setFromCamera( mouse, camera );
	let intersects = raycaster.intersectObjects(scene.children);
	for(let i = 0; i<intersects.length; i++) {
	    let curr = intersects[i].object
	    let oldColor = new THREE.Color(curr.material.color)
	    if(!objectColors[curr.uuid]) {
		objectColors[curr.uuid] = oldColor
	    }
	    objects.push(curr)
            let idStr = curr.name.replace('object', 'text');
	    let elements = document.getElementsByName(idStr)
	    elements.forEach((element) => {
		text.push(element)
	    })
		
	    
	}

    }

    changed.text.forEach((c) => c.style.backgroundColor = "#dddddd")
    changed.objects.forEach((c) => c.material.color.setHex(objectColors[c.uuid].getHex()))

    text.forEach((c) => c.style.backgroundColor = "yellow")
    objects.forEach((c) => c.material.color.setHex( 0xfffa00 ))

    changed.text = text
    changed.objects = objects
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

function onKeyDown( event ) {
    if(event.keyCode == 37) {
	anim_index = anim_index === 0 ? anim_index : anim_index - 1
    }
    else if(event.keyCode == 39) {
	anim_index = anim_index === scenes.length-1 ? anim_index : anim_index + 1
    }
}

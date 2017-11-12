
let renderer = new THREE.WebGLRenderer({ antialias: true });

let UIState = {
    mouse: {x:1000, y:10000},
    mousedown: false,
    mouseup: true,

    scene: null,
    camera: new THREE.PerspectiveCamera( 75, 1, 1, 1000 ),

    size: Math.min(window.innerWidth*0.65, window.innerHeight),

    canvasRect: null,

    hot: {},
    active: null
    
}

function init() {
    
    renderer.setSize(UIState.size, UIState.size)
    document.body.appendChild( renderer.domElement )
    UIState.camera.position.set(0, 0, 20 );

    UIState.canvasRect = renderer.domElement.getBoundingClientRect()


    // Register listeners
    document.addEventListener( 'mousemove', onMouseMove, false );
    
    mainLoop()
}

function mainLoop() {
    UIState.scene = new THREE.Scene()
    
    render() // Defined by user

    renderer.render( UIState.scene, UIState.camera )

    requestAnimationFrame(mainLoop)
}

function isHot(name) {
    let hot = UIState.hot[name]
    return hot ? true : false
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

// NDC stands for normalized device coordinates
function NDCtoWorld(x, y) {
    let ndcVec = new THREE.Vector2(x, y)
    let plane = new THREE.Plane(new THREE.Vector3(0,0,1))
    let raycaster = new THREE.Raycaster()
    raycaster.setFromCamera( ndcVec, UIState.camera )
    let pos = raycaster.ray.intersectPlane(plane)
    return pos
}

function underMouse(object) {
    let raycaster = new THREE.Raycaster()
    raycaster.setFromCamera( UIState.mouse, UIState.camera )
    let intersects = raycaster.intersectObjects([object])
    return intersects.length > 0
}



/*************************************

           Event Listeners

*************************************/

function onMouseMove( event ) {
    let canvasRect = UIState.canvasRect
    let size = UIState.size
    
    let xgood = event.clientX > canvasRect.left && event.clientX < canvasRect.right
    let ygood = event.clientY > canvasRect.top  && event.clientY < canvasRect.bottom

    if(xgood && ygood) {
	UIState.mouse.x = ((event.clientX - canvasRect.left) / size ) * 2 - 1;
	UIState.mouse.y = - ( (event.clientY - canvasRect.top) / size ) * 2 + 1;
    }
}


/*************************************

         Drawing Primitives

*************************************/


function drawPoint(ident, point, color) {
    // Point has an x and a y attribute in NDC coordinates
    let PARTICLE_SIZE = 0.5

    let name = "object_point_" + ident.toString()
    let vertex = NDCtoWorld(point.x, point.y)
    let geometry = new THREE.Geometry();
    geometry.vertices.push(vertex)

    let hot = isHot(name)
    
    
    let material = new THREE.PointsMaterial({ size: PARTICLE_SIZE, color: color })

    let particle = new THREE.Points( geometry, material )
    particle.material.depthTest = false
    particle.renderOrder = 1000

    particle.name = name

    if(underMouse(particle)) {
	if(!hot) {
	    if(UIState.active === null) {
		UIState.hot[name] = true
		hot = true
	    }
	}
    } else {
	if(hot) {
	    UIState.hot[name] = false
	    hot = false
	}
    }
    
    if(hot) {
	particle.material.color.set("yellow")
    }

    UIState.scene.add(particle)
    
}


function drawLine(ident, p1, p2, color) {
    let wp1 = NDCtoWorld(p1.x, p1.y)
    let wp2 = NDCtoWorld(p2.x, p2.y)

    let name = "object_line_" + ident.toString()

    let hot = isHot(name)

    let g = new THREE.Geometry()
    g.vertices.push(wp1, wp2)
    let m = new THREE.MeshBasicMaterial( { color: color } )

    let line  = new THREE.Line(g,m)
    line.name = name
    
    if(underMouse(line)) {
	if(!hot) {
	    if(UIState.active === null) {
		UIState.hot[name] = true
		hot = true
	    }
	}
    } else {
	if(hot) {
	    UIState.hot[name] = false
	    hot = false
	}
    }
    
    if(hot) {
	line.material.color.set("yellow")
    }

    UIState.scene.add(line)
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



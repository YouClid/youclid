
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
    
    if(dist(UIState.mouse, point) < 0.04) {
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
	color = "yellow"
    }
    let material = new THREE.PointsMaterial({ size: PARTICLE_SIZE, color: color })

    let particle = new THREE.Points( geometry, material )
    particle.material.depthTest = false
    particle.renderOrder = 1000

    particle.name = name

    UIState.scene.add(particle)
    
}



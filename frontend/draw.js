const vertexShader = `
attribute vec4 a_Position;
void main() {
     gl_Position = a_Position;
     gl_PointSize = 10.0;
}
`

const fragmentShader = `
void main() {
     gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
`


let UIState = {
    mouse: {x:1000, y:10000},
    mousedown: false,
    mouseup: true,

    gl: null,
    glData: null,

    drawn: {},

    size: Math.min(window.innerWidth*0.65, window.innerHeight),

    canvasRect: null,

    hot: {},
    active: null
    
}

function init() {

    let canvas = document.createElement('canvas')
    document.body.appendChild( canvas )
    canvas.width = UIState.size
    canvas.height = UIState.size
    
    let gl = canvas.getContext('webgl')
    let program = initShaders(gl, vertexShader, fragmentShader)
    gl.program = program
    gl.useProgram(program)

    let buf = gl.createBuffer()
    gl.bindBuffer(gl.ARRAY_BUFFER, buf)
    UIState.glData = new Float32Array(1024)

    UIState.gl = gl
    
    UIState.canvasRect = canvas.getBoundingClientRect()


    // Register listeners
    document.addEventListener( 'mousemove', onMouseMove, false );
    
    mainLoop()
}

function mainLoop() {
    let gl = UIState.gl
    gl.clearColor(0.0, 0.0, 0.0, 1.0)
    gl.clear(gl.COLOR_BUFFER_BIT)
    
    render() // Defined by user

    
    for(prop in UIState.drawn) {
	UIState.drawn[prop] = false
    }

    

    // requestAnimationFrame(mainLoop)
}

function isHot(name) {
    let hot = UIState.hot[name]
    return hot ? true : false
}

function initShaders(gl, vertSrc, fragSrc) {
    let vshader = gl.createShader(gl.VERTEX_SHADER)
    let fshader = gl.createShader(gl.FRAGMENT_SHADER)

    gl.shaderSource(vshader, vertSrc)
    gl.shaderSource(fshader, fragSrc)

    gl.compileShader(vshader)
    gl.compileShader(fshader)


    if (!gl.getShaderParameter(vshader, gl.COMPILE_STATUS)) {
	alert('An error occurred compiling the shaders: ' + gl.getShaderInfoLog(vshader));
	return null;
    }
    if (!gl.getShaderParameter(fshader, gl.COMPILE_STATUS)) {
	alert('An error occurred compiling the shaders: ' + gl.getShaderInfoLog(fshader));
	return null;
    }


    const shaderProgram = gl.createProgram();
    gl.attachShader(shaderProgram, vshader);
    gl.attachShader(shaderProgram, fshader);
    gl.linkProgram(shaderProgram);

    var success = gl.getProgramParameter(shaderProgram, gl.LINK_STATUS);
    if (!success) {
	// something went wrong with the link
	throw ("program filed to link:" + gl.getProgramInfoLog (shaderProgram));
    }

    return shaderProgram
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
    return false
}


function removeOldObjects() {
    let objects = UIState.scene.children
    let drawn = UIState.drawn
    let remove = objects.filter((o) => !drawn[o.name])
    remove.forEach((o) => UIState.scene.remove(o))

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
    let name = "object_point_" + ident.toString()
    UIState.drawn[name] = true

    let hot = isHot(name)

     if(underMouse(point)) {
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
	color = 'yellow'
    } 
    
    let gl = UIState.gl
    let data = UIState.glData

    let vertices = [
	point.x, point.y, 0.0, 1.0
    ]

    data.set(vertices)

    gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
    let a_Position = gl.getAttribLocation(gl.program, "a_Position")
    gl.enableVertexAttribArray(a_Position)
    gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 0, 0)

    gl.drawArrays(gl.POINTS, 0, 1)
    
}


function drawLine(ident, p1, p2, color) {

    let name = "object_line_" + ident.toString()
    UIState.drawn[name] = true

    let hot = isHot(name)
    
    if(underMouse(p1)) {
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

    
    let gl = UIState.gl
    let data = UIState.glData

    let vertices = [
	p1.x, p1.y, 0.0, 1.0,
	p2.x, p2.y, 0.0, 1.0
    ]
    
    data.set(vertices)
    

    gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
    let a_Position = gl.getAttribLocation(gl.program, "a_Position")
    gl.enableVertexAttribArray(a_Position)
    gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 0, 0)

    gl.drawArrays(gl.LINES, 0, 2)

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



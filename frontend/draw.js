const vertexShader = `
precision mediump float;
attribute vec4 a_Position;
attribute vec4 a_Color;
varying vec4 v_Color;
void main() {
     gl_Position = a_Position;
     gl_PointSize = 10.0;
     v_Color = a_Color;
}
`

const fragmentShader = `
precision mediump float;
varying vec4 v_Color;
void main() {
     gl_FragColor = v_Color;
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

    requestAnimationFrame(mainLoop)
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
    // World is now represented in NDC
    return {x:x, y:y}
}

function pointUnderMouse(point) {
    let sz = 5.0/(2*UIState.size)
    let center = {x:point.x+(sz/2), y:point.y+(sz/2)}
    return dist(UIState.mouse, center) < 0.06
}

function lineUnderMouse(p0, p1) {
    let mouse = UIState.mouse
    let n = sub(p1, p0)
    let a = p0
    let a_to_m = sub(mouse, a)
    let coeff = dot(n, a_to_m)/normsq(n)
    if(coeff < 0 || coeff > 1) {
	return false
    }
    let d = dist(a_to_m, scale(n, coeff))
    return d < 0.05
}

function polyUnderMouse(points) {
    if(points.length < 2) {
	return false
    }
    for(let i = 0; i<points.length; i++) {
	let next = (i+1)%points.length
	let p0 = points[i]
	let p1 = points[next]
	if(lineUnderMouse(p0, p1)) {
	    return true
	}
    }
    return false
}


function removeOldObjects() {
    let objects = UIState.scene.children
    let drawn = UIState.drawn
    let remove = objects.filter((o) => !drawn[o.name])
    remove.forEach((o) => UIState.scene.remove(o))

}

function flatten(arr) {
    return [].concat.apply([], arr);
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

        Geometric Predicates

*************************************/


function v2(x, y) {
    return {x:x, y:y}
}

function dot(v1, v2) {
    return (v1.x*v2.x)+(v1.y*v2.y)
}

function add(v1, v2) {
    return {
	x: v1.x+v2.x,
	y: v1.y+v2.y
    }
}

function sub(v1, v2) {
    return {
	x: v1.x-v2.x,
	y: v1.y-v2.y
    }
}

function normsq(v) {
    return dot(v,v)
}

function norm(v) {
    return Math.sqrt(normsq(v))
}

function scale(v, c) {
    return v2(v.x*c, v.y*c)
}



/*************************************

         Drawing Primitives

*************************************/


function drawPoint(ident, point, color) {
    // Point has an x and a y attribute in NDC coordinates
    let gl = UIState.gl
    let name = "object_point_" + ident.toString()
    UIState.drawn[name] = true

    let hot = isHot(name)

     if(pointUnderMouse(point)) {
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
	color = [1.0, 1.0, 0, 1.0]
    } 
    
    let vertices = [
	point.x, point.y, -0.1, 1.0
    ]
    vertices = vertices.concat(color)

    UIState.glData.set(vertices)

    gl.bufferData(gl.ARRAY_BUFFER, UIState.glData, gl.DYNAMIC_DRAW)
    let a_Position = gl.getAttribLocation(gl.program, "a_Position")
    gl.enableVertexAttribArray(a_Position)
    gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 8*4, 0)

    let a_Color = gl.getAttribLocation(gl.program, "a_Color")
    gl.enableVertexAttribArray(a_Color)
    gl.vertexAttribPointer(a_Color, 4, gl.FLOAT, false, 8*4, 4*4)

    gl.drawArrays(gl.POINTS, 0, 1)
    
}


function drawLine(ident, p1, p2, color) {

    let name = "object_line_" + ident.toString()
    UIState.drawn[name] = true

    let hot = isHot(name)
    
    if(lineUnderMouse(p1, p2)) {
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
	color = [1.0, 1.0, 0, 1.0] // Yellow
    }

    
    let gl = UIState.gl
    let data = UIState.glData

    let FSIZE = data.BYTES_PER_ELEMENT

    let v1 = [
	p1.x, p1.y, 0.0, 1.0
    ]
    v1 = v1.concat(color)
    let v2 = [
	p2.x, p2.y, 0.0, 1.0
    ]
    v2 = v2.concat(color)

    let vertices = v1.concat(v2)
    
    data.set(vertices)

    gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
    let a_Position = gl.getAttribLocation(gl.program, "a_Position")
    gl.enableVertexAttribArray(a_Position)
    gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 8*FSIZE, 0)

    let a_Color = gl.getAttribLocation(gl.program, "a_Color")
    gl.enableVertexAttribArray(a_Color)
    gl.vertexAttribPointer(a_Color, 4, gl.FLOAT, false, 8*FSIZE, 4*FSIZE)

    gl.drawArrays(gl.LINES, 0, 2)

}

function getPoints(center, radius) {
    let points = []
    let theta = 0
    let inc = 0.05
    let tau = 2*Math.PI
    while(theta <= tau) {
	let x = radius*Math.cos(theta)
	let y = radius*Math.sin(theta)
	points.push(add(v2(x, y), center))
	theta += inc
    }
    let x = radius*Math.cos(0)
    let y = radius*Math.sin(0)
    points.push(add(v2(x, y), center))
    return points
}

function drawCircle(ident, center, radius, color) {

    let name = "object_line_" + ident.toString()
    UIState.drawn[name] = true

    let hot = isHot(name)

    let points = getPoints(center, radius)
    
    if(polyUnderMouse(points)) {
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
	color = [1.0, 1.0, 0, 1.0] // Yellow
    }

    
    let gl = UIState.gl
    let data = UIState.glData

    let FSIZE = data.BYTES_PER_ELEMENT

    let vertices = points.map((p) => {
	return [p.x, p.y, 0.0, 1.0].concat(color)
    })
    
    data.set(flatten(vertices))

    gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
    let a_Position = gl.getAttribLocation(gl.program, "a_Position")
    gl.enableVertexAttribArray(a_Position)
    gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 8*FSIZE, 0)

    let a_Color = gl.getAttribLocation(gl.program, "a_Color")
    gl.enableVertexAttribArray(a_Color)
    gl.vertexAttribPointer(a_Color, 4, gl.FLOAT, false, 8*FSIZE, 4*FSIZE)

    gl.drawArrays(gl.LINE_STRIP, 0, points.length+1)

}


function drawPoly(ident, points, color) {

    let name = "object_line_" + ident.toString()
    UIState.drawn[name] = true

    let hot = isHot(name)
    
    if(polyUnderMouse(points)) {
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
	color = [1.0, 1.0, 0, 1.0] // Yellow
    }

    
    let gl = UIState.gl
    let data = UIState.glData

    let FSIZE = data.BYTES_PER_ELEMENT

    points.push(points[0])

    let vertices = points.map((p) => {
	return [p.x, p.y, 0.0, 1.0].concat(color)
    })
    
    data.set(flatten(vertices))

    gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
    let a_Position = gl.getAttribLocation(gl.program, "a_Position")
    gl.enableVertexAttribArray(a_Position)
    gl.vertexAttribPointer(a_Position, 4, gl.FLOAT, false, 8*FSIZE, 0)

    let a_Color = gl.getAttribLocation(gl.program, "a_Color")
    gl.enableVertexAttribArray(a_Color)
    gl.vertexAttribPointer(a_Color, 4, gl.FLOAT, false, 8*FSIZE, 4*FSIZE)

    gl.drawArrays(gl.LINE_STRIP, 0, points.length)

}



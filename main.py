Web VPython 3.2

scene.autoscale = False
scene.range = 4
scene.center = vec(2.5, 0.5, 0)

# helpful math functions
def get_angle(p1, p2):
    dir_vector = p2-p1
    angle = diff_angle(dir_vector, vec(1, 0, 0))
    # limit it between 0 and 2pi
    while angle < 0:
        angle += 2 * pi
    while angle > 2 * pi:
        angle -= 2 * pi
    
    return angle
    
# returns normal representing the perpendicular line intersecting the line connecting p1 and p2
def get_perpendicular(p1, p2):
    look_dir = norm(p2-p1)
    perp_dir = rotate(look_dir, angle=pi/2)
    
    return perp_dir
    

# path generation logic
def generate_hill_points(percent_semi_circle, radius, y_coord, x_coord, hill_height, num_points, left_curve_amount=1.5):
    c_points = []
    connection_width = 2 # connecting line width
    circle_range = sqrt(radius) * percent_semi_circle # how much to the left and right to draw the "circle"
    c1_start = x_coord-(radius+circle_range+left_curve_amount) # start of the first curve
    c_start = x_coord-(circle_range)# start of drawing the circle
    c2_start = x_coord+circle_range # start of drawing the 2nd curve
    
    hill_width = (radius+circle_range)-c1_start
    
    for i in range(num_points):
        percent_done = i/num_points # percent done with drawing
        cx = c1_start + (hill_width*percent_done) # current x coordinate
        
        if (cx > c2_start):
            c_points.push(
                vec(
                    cx+connection_width, 
                    (hill_height/radius) * ((cx - x_coord - radius - circle_range)**2) - (hill_height * radius - sqrt(radius - circle_range**2)) + y_coord, 
                    0
                )
            )
        elif (cx > c_start):
            c_points.push(
                vec(
                    cx+connection_width,
                    sqrt(radius-(cx-x_coord)**2)+y_coord,
                    0
                )    
            )
        elif (cx > c1_start):
            offset = 0
            if cx > c1_start + left_curve_amount:
                offset = connection_width
            
            c_points.push(
                vec(
                    cx + offset, 
                    (hill_height/radius) * ((cx - x_coord + radius + circle_range)**2) - (hill_height * radius - sqrt(radius - circle_range**2)) + y_coord, 
                    0
                )
            )
    return (c_points, vec(x_coord, y_coord, 0), { 'start': c_start, 'end': c2_start } )

def draw_line(p1, p2, num_points):
    slope = (p2 - p1)/(num_points - 1)
    ps = [p1]
    for i in range(1, num_points):
        ps.append(ps[i-1] + slope)

    return ps

def generate_path(left_curve_amount, percent_semi_circle, radius, y_coord, x_coord, hill_height, hill_points):
    hill_radius = 1
    hill_points, circle_center, circle_range = generate_hill_points(
        percent_semi_circle=percent_semi_circle, 
        radius=radius, 
        y_coord=y_coord, 
        x_coord=x_coord, 
        hill_height=hill_height,
        num_points=hill_points,
        left_curve_amount=left_curve_amount
    )
    bottom_1 = hill_points[0].y
    bottom_2 = hill_points[len(hill_points)-1].y
    
    cart_path = hill_points + draw_line(
        hill_points[len(hill_points)-1] + vec(0.01, 0, 0),  # need to have a vector because having two of the same point breaks the program (xdist = 0, division by 0)
        vec(
            hill_points[len(hill_points)-1].x+5, bottom_2, 0
        ), 
        30
    )
    
    return (cart_path, circle_center, circle_range)

# object generation logic
def generate_cart():
    cart_length = 0.4
    cart_width = 0.2
    cart_height = 0.15
    thickness = 0.02
    offset = thickness/2
    
    left_box = box(size=vec(thickness, cart_height, cart_width), pos=vec(-cart_length/2 + offset, 0, 0))
    right_box = box(size=vec(thickness, cart_height, cart_width), pos=vec(cart_length/2 - offset, 0, 0))
    back_box = box(size=vec(cart_length, cart_height, thickness), pos=vec(0, 0, -cart_width/2 + offset))
    forward_box = box(size=vec(cart_length, cart_height, thickness), pos=vec(0, 0, cart_width/2 - offset))
    bottom_box = box(size=vec(cart_length, thickness, cart_width), pos=vec(0, -cart_height/2 + offset, 0))
    
    cart = compound([left_box, right_box, back_box, forward_box, bottom_box])
    return cart

# path variables
left_curve_amount = 1.5
hill_radius = 1

cart_path, circle_center, circle_range = generate_path(
    left_curve_amount=left_curve_amount,
    percent_semi_circle=0.96,
    radius=hill_radius,
    y_coord=0,
    x_coord=0,
    hill_height=2,
    hill_points=150
)

path_curve = curve(pos=cart_path)

# physics variables
dt = 0.01
dx = 0.5
g = 9.81
initial_height = cart_path[0].y

# object variables

initial_kinetic_energy = 0.00001
cart = generate_cart()
cart.weight = 10 # kg
cart.angle = 0 # radians
cart.kinetic_energy = initial_kinetic_energy
cart.direction = 1
cart.pos = cart_path[0]

# loop variables
path_completed = False
i = 0
while True:
    if not path_completed:
        while i < len(cart_path) - 1 and i >= 0:
            if i == 0 and cart.direction < 0:
                cart.direction = 1
                cart.kinetic_energy = initial_kinetic_energy
            
            p1 = cart_path[i]
            p2 = cart_path[i+cart.direction]
            
            going_down = p1.y > p2.y
            
            angle = get_angle(p1, p2)
            if going_down:
                angle *= -1
            if cart.direction < 0:
                angle += pi
                
            cart.rotate(axis=vec(0, 0, 1), angle=angle-cart.angle, origin=cart.pos)
            cart.angle = angle
            
            percent_travel = dx/mag(p2-p1) # how much progress of the path should each iteration make, this is to prevent reliance on # of points in path
            while cart.pos.x < p2.x if cart.direction > 0 else cart.pos.x > p2.x :
                rate(1/dt)
                
                velocity = sqrt((2 * abs(cart.kinetic_energy))/cart.weight)
                cart.pos += (p2-p1) * velocity * dt * percent_travel
                cart.kinetic_energy = g * cart.weight * (initial_height - cart.pos.y)
                
                if cart.kinetic_energy < 0:
                    cart.direction = -1
                
            cart.pos = p2
            i += cart.direction
            
        path_completed = True
    else:
        rate(1/dt)
            
    




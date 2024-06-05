Web VPython 3.2

scene.autoscale = False
scene.range = 4
scene.center = vec(2.5, 0.5, 0)

# helpful math functions

# limit angle between 0 and 2 PI
def simplify_angle(angle):
    while angle < 0:
        angle += 2 * pi
    while angle > 2 * pi:
        angle -= 2 * pi
    return angle

def get_angle(p1, p2):
    dir_vector = p2-p1
    angle = diff_angle(dir_vector, vec(1, 0, 0))
    
    return simplify_angle(angle)
    
# returns normal representing the perpendicular line intersecting the line connecting p1 and p2
def get_perpendicular(p1, p2):
    look_dir = norm(p2-p1)
    perp_dir = rotate(look_dir, angle=pi/2)
    
    return perp_dir

def update_cat(cart, cat, p1, p2):
    cat.pos = cart.pos + get_perpendicular(p1, p2) * 0.2 * cart.direction

def get_points_above(path, cat):
    for i in range(len(path)):
        point = path[i]
        if cat.pos.x < point.x:
            return [path[i-1], point]
            
def path_intersect(path, cat):
    above_points = get_points_above(path, cat)
    avg_y = (above_points[0].y + above_points[1].y)/2
    threshold = 0.001
    
    if cat.velocity.y > 0:
        return (False, above_points)
    
    return (cat.pos.y-avg_y-(cat.height/2) < threshold, above_points)
    

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
    return (c_points, vec(x_coord + connection_width, y_coord + connection_width, 0), { 'start': c_start + connection_width, 'end': c2_start + connection_width } )

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
    
    left_box = box(size=vec(thickness, cart_height, cart_width), pos=vec(-cart_length/2 + offset, 0, 0), color=color.green)
    right_box = box(size=vec(thickness, cart_height, cart_width), pos=vec(cart_length/2 - offset, 0, 0), color=color.green)
    back_box = box(size=vec(cart_length, cart_height, thickness), pos=vec(0, 0, -cart_width/2 + offset), color=color.green)
    forward_box = box(size=vec(cart_length, cart_height, thickness), pos=vec(0, 0, cart_width/2 - offset), color=color.green)
    bottom_box = box(size=vec(cart_length, thickness, cart_width), pos=vec(0, -cart_height/2 + offset, 0), color=color.green)
    
    cart = compound([left_box, right_box, back_box, forward_box, bottom_box])
    return cart

def generate_cat():
    cat_radius = 0.15
    cat_head = sphere(radius=cat_radius, pos=vec(0, 0, 0), color=color.orange)
    cat_left_ear = cone(radius=0.1, pos=vec(-cat_radius/2, cat_radius/1.5, 0), color=color.orange, length=cat_radius)
    cat_right_ear = cone(radius=0.1, pos=vec(cat_radius/2, cat_radius/1.5, 0), color=color.orange, length=cat_radius)
    cat_left_ear.rotate(axis=vec(0, 0, 1), angle=pi/2, origin=cat_left_ear.pos)
    cat_right_ear.rotate(axis=vec(0, 0, 1), angle=pi/2, origin=cat_right_ear.pos)
    cat_left_eye = sphere(radius=cat_radius/4, pos=vec(-cat_radius/3, 0, cat_radius), color=color.black)
    cat_right_eye = sphere(radius=cat_radius/4, pos=vec(cat_radius/3, 0, cat_radius), color=color.black)
    
    cat = compound([cat_head, cat_left_ear, cat_right_ear, cat_left_eye, cat_right_eye])
    return cat

# path variables
left_curve_amount = 1.22
hill_radius = 1

# physics variables
dt = 0.01
dx = 0.5
g = 9.81

# user input
def reset_scene():
    global reset, cart, cat, path_completed, path_curve, cart_path, circle_center, circle_range
    cart.visible = False
    cat.visible = False
    path_curve.visible = False
    
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
    
    cart = generate_cart()
    cat = generate_cat()
    path_completed = False
    reset = True
def set_left_curve(evt):
    global left_curve_amount, left_curve_text
    left_curve_amount = evt.value
    left_curve_text.text = 'left curve: {:1.2f}'.format(evt.value)
    
    reset_scene()
reset_button = button(text='reset', bind=reset_scene, pos=scene.title_anchor)
left_curve_slider = slider(min=0.5, max=3, value=left_curve_amount, bind=set_left_curve)
left_curve_text = wtext(text='left curve: {:1.2f}'.format(left_curve_slider.value))

scene.append_to_caption('\n')

# persistent variables
reset = False
path_completed = False
cart = generate_cart()
cat = generate_cat()

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

while True:
    if not path_completed:
        # set scene
        scene.autoscale = False
        scene.range = 4
        scene.center = vec(2.5, 0.5, 0)
        
        
        
        # object variables

        initial_height = cart_path[0].y
        initial_kinetic_energy = 0.00001
        
        cart.weight = 10 # kg
        cart.angle = 0 # radians
        cart.kinetic_energy = initial_kinetic_energy
        cart.direction = 1
        cart.pos = cart_path[0]
        
        cat.weight = 1 # kg
        cat.in_cart = True
        cat.grounded = False
        cat.angle = 0
        cat.has_said_feeling = False
        cat.velocity = vec(0, 0, 0)
        update_cat(cart, cat, cart_path[0], cart_path[1])
        
        # loop variables
        i = 0
    
        while i < len(cart_path) - 1 and i >= 0:
            if reset:
                break
            
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
            
            angle = simplify_angle(angle)
                
            cart.rotate(axis=vec(0, 0, 1), angle=angle-cart.angle, origin=cart.pos)
            
            if cat.in_cart:
                cat.rotate(axis=vec(0, 0, 1), angle=angle-cart.angle, origin=cat.pos)
                cat.angle = angle
                
            cart.angle = angle
            
            percent_travel = dx/mag(p2-p1) # how much progress of the path should each iteration make, this is to prevent reliance on # of points in path
            rs = False
            while cart.pos.x < p2.x if cart.direction > 0 else cart.pos.x > p2.x:
                rate(1/dt)
                
                if reset:
                    rs = True
                    break
                
                apparent_weight = cart.weight
                if cat.in_cart:
                    apparent_weight += cat.weight
                
                velocity = sqrt((2 * abs(cart.kinetic_energy))/apparent_weight)
                cart.pos += (p2-p1) * velocity * dt * percent_travel
                
                if cat.in_cart:
                    update_cat(cart, cat, p1, p2)
                
                cart.kinetic_energy = g * apparent_weight * (initial_height - cart.pos.y)
                
                if cart.kinetic_energy < 0:
                    cart.direction = -1
                
                if not cat.in_cart:
                    # kinematics here
                    if not cat.grounded:
                        cat.pos += cat.velocity * dt * dx
                        cat.velocity -= g * vec(0, 1, 0) * dt
                        
                        is_intersect, above_points = path_intersect(cart_path, cat)
                        
                        if is_intersect:
                            cat.grounded = True
                        
                elif circle_range['start'] < cat.pos.x and cat.pos.x < circle_range['end'] and not cat.grounded:
                    # centripetal force calculation here
                    centrifugal_force = cat.weight * velocity ** 2 / hill_radius
                    gravity_normal = vec(0, 1, 0)
                    center_to_cat = norm(cat.pos - circle_center)
                    centripetal_force = cat.weight * g * abs(dot(gravity_normal, center_to_cat))
                    
                    if centrifugal_force > centripetal_force:
                        # use timeless distance equation to check if max y value is enough to "jump" out of the cart
                        # vf^2 = vi^2 + 2ad where vf = 0, 0 = vi^2 - 2gd, 2gd = vi^2, d = vi^2/(2g)
                        # must multiply by "dx" because in this program, dx is used to adjust the scale of values in each loop
                        # NOTE: cart also moves upward so find the point the cat is above at that time and thats the y position of the cart
                        exit_velocity = velocity * vec(cos(cat.angle), sin(cat.angle), 0)
                        distance_upward = ((exit_velocity.y * dx)**2)/(2 * g)
                        future_x = cat.pos.x + (exit_velocity.y/g) * exit_velocity.x
                            
                        # if no abovepoint, it means the cat went REALLY REALLY far
                        if distance_upward < (cart.height + cat.height/2):
                            if not cat.has_said_feeling:
                                cat.has_said_feeling = True
                        else:
                            cat.in_cart = False
                            
                            cat.velocity = exit_velocity
                
            cart.pos = p2
            if cat.in_cart:
                update_cat(cart, cat, p1, p2)
                
            i += cart.direction
            if rs:
                break
        if not reset:
            path_completed = True
        
            while not cat.grounded:
                rate(1/dt)
                
                cat.pos += cat.velocity * dt * dx
                cat.velocity -= g * vec(0, 1, 0) * dt
                
                if cat.pos.y < 0:
                    break
            cat.visible = False
            print("cat exploded")
        else:
            reset = False
    else:
        rate(1/dt)
            
    




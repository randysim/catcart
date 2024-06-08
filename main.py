Web VPython 3.2

scene.autoscale = False
scene.range = 4
scene.center = vec(2.5, 0.5, 0)
DEBUG = True
point_every = 0.05

# HELPFUL MATH FUNCTIONS ======================

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
    direction = 1
    if p1.x > p2.x:
        direction = -1
    cat.pos = cart.pos + get_perpendicular(p1, p2) * 0.2 * direction

def get_points_above(path, cat):
    for i in range(len(path)):
        point = path[i]
        if cat.pos.x < point.x:
            return [path[i-1], point]
            
def path_intersect(path, cat):
    above_points = get_points_above(path, cat)
    if not above_points:
        return (False, None)
    
    avg_y = (above_points[0].y + above_points[1].y)/2
    threshold = 0.001
    
    if cat.velocity.y > 0:
        return (False, above_points)
    
    return (cat.pos.y-avg_y-(cat.height/2) < threshold, above_points)
    

# PATH GENERATION LOGIC =====================

# path types
# - HILL
# - LINE
# - LEFT_CURVE

def generate_hill(percent_semi_circle, radius, hill_height, starting_pos=None, y_coord=0, x_coord=0):
    c_points = []
    circle_range = sqrt(radius) * percent_semi_circle # how much to the left and right to draw the "circle"
    c1_start = x_coord-(radius+circle_range) # start of the first curve
    c_start = x_coord-(circle_range)# start of drawing the circle
    c2_start = x_coord+circle_range # start of drawing the 2nd curve
    
    hill_width = (radius+circle_range)-c1_start
    num_points = int(1.5 * hill_width/point_every)
    offset = vec(0, 0, 0)
    
    for i in range(num_points):
        percent_done = i/num_points # percent done with drawing
        cx = c1_start + (hill_width*percent_done) # current x coordinate
        
        if (cx > c2_start):
            c_points.append(
                vec(
                    cx, 
                    (hill_height/radius) * ((cx - x_coord - radius - circle_range)**2) - (hill_height * radius - sqrt(radius - circle_range**2)) + y_coord, 
                    0
                ) + offset
            )
        elif (cx > c_start):
            c_points.append(
                vec(
                    cx,
                    sqrt(radius-(cx-x_coord)**2)+y_coord,
                    0
                ) + offset 
            )
        elif (cx >= c1_start):
            c_points.append(
                vec(
                    cx, 
                    (hill_height/radius) * ((cx - x_coord + radius + circle_range)**2) - (hill_height * radius - sqrt(radius - circle_range**2)) + y_coord, 
                    0
                ) + offset
            )
        if i == 0 and starting_pos:
            offset = starting_pos - c_points[i]
            c_points[i] = starting_pos
            
    return (c_points, { 'start': c_start + offset.x, 'end': c2_start + offset.x, 'type': "HILL", 'center': vec(x_coord + offset.x, y_coord + offset.y, 0), 'radius': radius  })

def generate_left_curve(initial_height, starting_pos=None):
    c_points = []
    left_curve_amount = sqrt(initial_height)
    num_points = int(left_curve_amount/point_every)
    cx = -left_curve_amount
    dx = left_curve_amount/(num_points-1)
    
    i = 0
    offset = vec(0, 0, 0)
        
    for i in range(num_points):
        c_points.append(vec(cx, cx ** 2, 0) + offset)
        
        if i == 0 and starting_pos:
            offset = starting_pos - c_points[i]
            c_points[i] = starting_pos
        cx += dx
    return c_points
    
    
def generate_line(p1, p2, starting_pos=None):
    num_points = int((p2.x-p1.x)/point_every) + 1
    slope = (p2 - p1)/(num_points - 1)
    ps = [p1]
    
    offset = vec(0, 0, 0)
    if starting_pos:
        offset = starting_pos - ps[0]
        ps[0] = starting_pos
        
    for i in range(1, num_points):
        ps.append(ps[i-1] + slope)
            
    return ps
 
def generate_dip(curvature, height, starting_pos=None):
    width = 1
    num_points = width/point_every + 1
    cx = -width/2
    dx = width/(num_points-1)
    
    c_points = []
    offset = vec(0, 0, 0)
    
    for i in range(num_points):
        cy = -height/(1 + exp(1)**(-curvature * cx))
        c_points.append(vec(cx, cy, 0) + offset)
        
        if i == 0 and starting_pos:
            offset = starting_pos - c_points[i]
            c_points[i] = starting_pos
        cx += dx
    return c_points

def generate_path(components):
    points = []
    c_ranges = []
    settings = {} # settings for each segment of the path
    
    for i in range(len(components)):
        component = components[i]
        starting_pos = None
        if i != 0:
            starting_pos = points[-1]
        
        def delete_segment(evt, i=i):
            nonlocal settings, components
            for widget in settings[i].values():
                widget.delete()
            settings.pop(i)
            components.pop(i)
            
            reset_scene(update_settings=True)

        if component['type'] == 'LEFT_CURVE':
            points += generate_left_curve(component['initial_height'], starting_pos=starting_pos)
            
            if not component.get('rendered_settings'):
                path_label = wtext(text=str(i) + ') left curve ') 
                initial_height_text = wtext(text='initial height: {:1.2f}'.format(component['initial_height']))
                # 2nd parameter is to "capture" i into this iteration of the function
                def update_initial_height(evt, i=i):
                    nonlocal components, initial_height_text # like "global" but raises scope to next non-global scope
                    components[i]['initial_height'] = evt.value
                    initial_height_text.text = 'initial height: {:1.2f}'.format(evt.value)
                    
                    reset_scene()
                
                settings[i] = {
                    'path_label': path_label,
                    'initial_height_slider': slider(min=0.5, max=10, value=component['initial_height'], bind=update_initial_height),
                    'initial_height_text': initial_height_text,
                    'delete_button': button(bind=delete_segment, text="delete")
                }
                
                component['rendered_settings'] = True
                scene.append_to_caption('\n')
                
        elif component['type'] == 'LINE':
            points += generate_line(vec(0, 0, 0), component['vector'], starting_pos=starting_pos)
            
            if not component.get('rendered_settings'):
                path_label = wtext(text=str(i) + ') line ') 
                x_direction_text = wtext(text="X: {:1.2f}".format(component['vector'].x))
                def update_x(evt, i=i):
                    nonlocal components, settings
                    components[i]['vector'].x = float(evt.value)
                    settings[i]['x_direction_text'].text = "X: {:1.2f}".format(evt.value)
                    reset_scene()
                x_direction_slider = slider(min=0, max=10, value=component['vector'].x, bind=update_x)
                
                y_direction_text = wtext(text="Y: {:1.2f}".format(component['vector'].y))
                def update_y(evt, i=i):
                    nonlocal components, settings
                    components[i]['vector'].y = float(evt.value)
                    settings[i]['y_direction_text'].text = "Y: {:1.2f}".format(evt.value)
                    reset_scene()
                y_direction_slider = slider(min=-10, max=10, value=component['vector'].y, bind=update_y)
                
                settings[i] = {
                    'path_label': path_label,
                    'x_direction_text': x_direction_text,
                    'y_direction_text': y_direction_text,
                    'x_direction_slider': x_direction_slider,
                    'y_direction_slider': y_direction_slider,
                    'delete_button': button(bind=delete_segment, text="delete")
                }
                
                component['rendered_settings'] = True
                scene.append_to_caption('\n')
                
        elif component['type'] == 'HILL':
            hill_path, hill_top = generate_hill(component['percent_semi_circle'], component['radius'], component['hill_height'], starting_pos=starting_pos)
            points += hill_path
            c_ranges += hill_top
            
            if not component.get('rendered_settings'):
                hill_label = wtext(text=str(i) + ") hill ")
                
                radius_text = wtext(text="radius: {:1.2f}".format(component['radius']))
                def update_radius(evt, i=i):
                    nonlocal components, settings
                    components[i]['radius'] = float(evt.value)
                    settings[i]['radius_text'].text = "radius: {:1.2f}".format(evt.value)
                    reset_scene()
                    
                radius_slider = slider(min=0.5, max=2, value=components[i]['radius'], bind=update_radius)
                
                settings[i] = {
                    'hill_label': hill_label,
                    'radius_text': radius_text,
                    'radius_slider': radius_slider,
                    'delete_button': button(bind=delete_segment, text="delete")
                }
                
                component['rendered_settings'] = True
                scene.append_to_caption('\n')
        elif component['type'] == 'DIP':
            points += generate_dip(component['curvature'], component['height'], starting_pos=starting_pos)
            
            if not component.get('rendered_settings'):
                dip_label = wtext(text=str(i) + ") dip ")
                curvature_text = wtext(text="radius: {:1.2f}".format(component['curvature']))
                def update_curvature(evt, i=i):
                    nonlocal components, settings
                    components[i]['curvature'] = float(evt.value)
                    settings[i]['curvature_text'].text = "curvature: {:1.2f}".format(evt.value)
                    reset_scene()
                    
                curvature_slider = slider(min=0, max=10, value=components[i]['curvature'], bind=update_curvature)
                
                height_text = wtext(text="height: {:1.2f}".format(component['height']))
                def update_height(evt, i=i):
                    nonlocal components, settings
                    components[i]['height'] = float(evt.value)
                    settings[i]['height_text'].text = "height: {:1.2f}".format(evt.value)
                    reset_scene()
                    
                height_slider = slider(min=0, max=3, value=components[i]['height'], bind=update_height)
                
                settings[i] = {
                    'dip_label': dip_label,
                    'curvature_text': curvature_text,
                    'curvature_slider': curvature_slider,
                    'height_text': height_text,
                    'height_slider': height_slider
                }
                
                component['rendered_settings'] = True
                scene.append_to_caption('\n')
            
            
    return (points, c_ranges, settings)

# OBJECT GENERATION LOGIC ============
# - default created invisible, make visible later
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
    
    cart = compound([left_box, right_box, back_box, forward_box, bottom_box], visible=False)
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
    
    cat = compound([cat_head, cat_left_ear, cat_right_ear, cat_left_eye, cat_right_eye],  visible=False)
    return cat

# USER INPUT ==========================
def reset_scene(update_settings=False):
    global reset, cart, cat, path_completed, path_curve, cart_path, circle_parts, path_components, running, toggle_button, settings
    cart.visible = False
    cat.visible = False
    path_curve.visible = False
    
    if update_settings:
        reset_widgets()
        cart_path, circle_parts, settings = generate_path(path_components)
    else:
        cart_path, circle_parts, _ = generate_path(path_components)
    
    path_curve = curve(pos=cart_path)
    
    cart = generate_cart()
    cat = generate_cat()
    running = False
    path_completed = False
    toggle_button.text = 'run cat'
    
    # enable widgets again
    set_widgets(disabled=False)
    
def reset_widgets():
    global path_components
    scene.caption = ""
    for component in path_components:
        component['rendered_settings'] = False
    
def reset_path():
    global path_components, toggle_button
    path_components = [
        { 'type': 'LEFT_CURVE', 'initial_height': 2 },
        { 'type': 'LINE', 'vector': vec(2, 0, 0) },
        { 'type': 'HILL', 'percent_semi_circle': 0.96, 'radius': 1, 'hill_height': 2 },
        { 'type': 'LINE', 'vector': vec(2, 0, 0) }
    ]
    
    reset_scene(update_settings=True)
    
    
def set_widgets(disabled):
    global settings
    
    for setting in settings.values():
        for widget in setting.values():
            if widget.disabled == True or widget.disabled == False:
                widget.disabled = disabled

def run(evt):
    global running, toggle_button
    
    if evt.text == 'run cat':
        running = True
        evt.text = 'stop cat'
        
        # disable widgets
        set_widgets(disabled=True)
    elif evt.text == 'stop cat':
        
        reset_scene(update_settings=True)

toggle_button = button(text='run cat', bind=run, pos=scene.title_anchor)
reset_path = button(text='reset path', bind=reset_path, pos=scene.title_anchor)


# VARIABLES ==========================================

# physics variables
dt = 0.01
dx = 0.5 # scale for how much distance is supposed to be "traveled" per interpolation
g = 9.81

# persistent variables
reset = False
path_completed = False
running = False
cart = generate_cart()
cat = generate_cat()

# path variables
path_components = [
    { 'type': 'LEFT_CURVE', 'initial_height': 2 },
    { 'type': 'LINE', 'vector': vec(2, 0, 0) },
    { 'type': 'HILL', 'percent_semi_circle': 0.96, 'radius': 1, 'hill_height': 2 },
    { 'type': 'DIP', 'curvature': 6.1, 'height': 0.5 },
    { 'type': 'LINE', 'vector': vec(2, 0, 0) }
]
cart_path, circle_parts, settings = generate_path(path_components)
path_curve = curve(pos=cart_path)

while True:
    if not path_completed and running:
        # set scene
        """
        scene.autoscale = False
        scene.range = 4
        scene.center = vec(2.5, 0.5, 0)
        """
        
        # object variables
        initial_height = cart_path[0].y
        initial_kinetic_energy = 0.00001
        
        cart.visible = True
        cat.visible = True
        
        cart.weight = 10 # kg
        cart.angle = 0 # radians
        cart.kinetic_energy = initial_kinetic_energy # joules
        cart.direction = 1 # 1 if right, -1 if left
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
        ci = 0 # counter for circular paths traversed
    
        while i < len(cart_path) - 1 and i >= 0:
            if not running:
                break
            
            if i == 0 and cart.direction < 0:
                cart.kinetic_energy = initial_kinetic_energy
            
            if ci < len(circle_parts) and cart.pos.x > circle_parts[ci]['end']:
                ci += 1
            
            p1 = cart_path[i]
            p2 = cart_path[i+cart.direction]
            # skip if two points are the same
            if p1.x == p2.x and p1.y == p2.y:
                i += cart.direction
                continue
            
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
            
            rs = False # reset variable to make it reset more responsively
            change_direction = False
            while cart.pos.x < p2.x if cart.direction > 0 else cart.pos.x > p2.x:
                rate(1/dt)
                
                if not running:
                    rs = True
                    break
                
                apparent_weight = cart.weight
                if cat.in_cart:
                    apparent_weight += cat.weight
                
                velocity = sqrt((2 * abs(cart.kinetic_energy))/apparent_weight)
                cart.pos += norm(p2-p1) * dx * velocity * dt
                
                if cat.in_cart:
                    update_cat(cart, cat, p1, p2)
                
                cart.kinetic_energy = g * apparent_weight * (initial_height - cart.pos.y)
                
                if not change_direction and cart.kinetic_energy < 0:
                    change_direction = True
                    cart.direction *= -1
                    temp = p2
                    p2 = p1
                    p1 = temp
                
                if not cat.in_cart:
                    # kinematics here
                    if not cat.grounded:
                        cat.pos += cat.velocity * dt * dx
                        cat.velocity -= g * vec(0, 1, 0) * dt
                        
                        is_intersect, above_points = path_intersect(cart_path, cat)
                        
                        if is_intersect:
                            if DEBUG:
                                print("cat hit ground")
                            cat.grounded = True
                        
                elif ci < len(circle_parts) and circle_parts[ci]['start'] < cat.pos.x and cat.pos.x < circle_parts[ci]['end'] and not cat.grounded:
                    # centripetal force calculation here
                    centrifugal_force = cat.weight * velocity ** 2 / circle_parts[ci]['radius']
                    gravity_normal = vec(0, 1, 0)
                    center_to_cat = norm(cat.pos - circle_parts[ci]['center'])
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
                        if distance_upward < (cart.height + cat.height/3):
                            if not cat.has_said_feeling:
                                if DEBUG:
                                    print("cat feel light")
                                cat.has_said_feeling = True
                        else:
                            cat.in_cart = False
                            if DEBUG:
                                print("cat go flying")
                            cat.velocity = exit_velocity

            cart.pos = p2
            if cat.in_cart:
                update_cat(cart, cat, p1, p2)
                
            i += cart.direction
            if rs:
                break

        if running:
            path_completed = True
        
            while not cat.in_cart and not cat.grounded:
                rate(1/dt)
                
                cat.pos += cat.velocity * dt * dx
                cat.velocity -= g * vec(0, 1, 0) * dt
                
                if cat.pos.y < 0:
                    break
            cat.visible = False
            
            if DEBUG:
                print("cat exploded")
            reset_scene()

    else:
        rate(1/dt)
            
    

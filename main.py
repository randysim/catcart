Web VPython 3.2

def generate_hill_points(percent_semi_circle, semi_radius, y_coord, x_coord, hill_height, num_points):
    c_points = []
    circle_range = sqrt(semi_radius) * percent_semi_circle # how much to the left and right to draw the "circle"
    c1_start = x_coord-(semi_radius+circle_range) # start of the first curve
    c_start = x_coord-(circle_range)# start of drawing the circle
    c2_start = x_coord+circle_range # start of drawing the 2nd curve
    
    hill_width = (semi_radius+circle_range)-c1_start
    
    for i in range(num_points):
        percent_done = i/num_points # percent done with drawing
        cx = c1_start + (hill_width*percent_done) # current x coordinate
        
        if (cx > c2_start):
            c_points.push(
                vec(
                    cx, 
                    (hill_height/semi_radius) * ((cx - x_coord - semi_radius - circle_range)**2) - (hill_height * semi_radius - sqrt(semi_radius - circle_range**2)) + y_coord, 
                    0
                )
            )
        elif (cx > c_start):
            c_points.push(
                vec(
                    cx,
                    sqrt(semi_radius-(cx-x_coord)**2)+y_coord,
                    0
                )    
            )
        elif (cx > c1_start):
            c_points.push(
                vec(
                    cx, 
                    (hill_height/semi_radius) * ((cx - x_coord + semi_radius + circle_range)**2) - (hill_height * semi_radius - sqrt(semi_radius - circle_range**2)) + y_coord, 
                    0
                )
            )
    return (c_points, {'x': x_coord, 'y': y_coord}, { 'start': c_start, 'end': c2_start })

initial_height = 1.5
starting_position = vec(-3.5, initial_height, 0)

hill_points, circle_center, circle_range = generate_hill_points(
    percent_semi_circle=0.96, 
    semi_radius=1, 
    y_coord=0, 
    x_coord=0, 
    hill_height=2,
    num_points=150
)
bottom_1 = hill_points[0].y
bottom_2 = hill_points[len(hill_points)-1].y

cart_path = [ starting_position, vec(hill_points[0].x-0.5, bottom_1, 0) ] + hill_points + [ vec(
        hill_points[len(hill_points)-1].x+0.5, bottom_2, 0
    ) ]

curve(pos=cart_path)

# SIMULATION
# weight in kg
cart_weight = 10
cat_weight = 1
total_weight = cart_weight + cat_weight

cat = box(
    pos=(cart_path[0]+vec(0,0.05,0)), 
    length=0.15, 
    width=0.2, 
    height=0.25, 
    color=color.orange
)
cart = box(
    pos=cart_path[0], 
    length=0.3, 
    width = 0.2, 
    height=0.2,
    color=color.green
)
cartcat = compound(
    [cat, cart]
)

dt = 0.01
dx=0.5
g = 9.81

# animation loop
# interpolate between points based on velocity calculated from KE

current_angle = 0
kinetic_energy = 10

for i in range(len(cart_path)-1):
    p1 = cart_path[i] # each point is a vector (xyz)
    p2 = cart_path[i+1]
    going_down = False
    if p1.y > p2.y:
        going_down = True
    
    y_dist = abs(p2.y-p1.y)
    x_dist = abs(p2.x-p1.x)
    
    angle = atan(y_dist/x_dist)
    if going_down:
        angle *= -1
    change = angle-current_angle
    
    cartcat.rotate(axis=vec(0, 0, 1), angle=change, origin=cartcat.pos)
    current_angle = angle
    
    percent_travel = dx/mag(p2-p1) 
    
    while cartcat.pos.x < p2.x:
        rate(1/dt)
        velocity = sqrt((2 * abs(kinetic_energy))/total_weight)
        cartcat.pos = cartcat.pos + (p2-p1) * velocity * dt * percent_travel
        kinetic_energy = g * total_weight * (initial_height - cartcat.pos.y)
    cartcat.pos = p2 # after finishing traveling path, just set the position to last point to be safe
    
    
    
    
    
    
    
    
    

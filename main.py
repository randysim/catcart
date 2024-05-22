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

initial_height = 1
starting_position = vec(-3.5, initial_height, 0)

hill_points, circle_center, circle_range = generate_hill_points(
    percent_semi_circle=0.96, 
    semi_radius=1, 
    y_coord=0, 
    x_coord=0, 
    hill_height=2, 
    num_points=150
)
bottom = hill_points[0].y
cart_path = [starting_position, vec(hill_points[0].x-0.5, bottom, 0)] + hill_points + [ vec(hill_points[len(hill_points)-1].x+0.5, bottom, 0) ]

curve(pos=cart_path)

# SIMULATION
# weight in kg
cart_weight = 10
cat_weight = 1

cart = box(pos=cart_path[0], length=0.3, width = 0.2, height=0.2)

dt = 0.01
for i in range(len(cart_path)-1):
    rate(1/dt)

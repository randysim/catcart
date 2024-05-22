Web VPython 3.2

def generate_hill_points(percent_semi_circle, semi_radius, y_coord, x_coord, hill_height, num_points):
    c_points = []
    circle_range = sqrt(semi_radius) * percent_semi_circle # how much to the left and right to draw the "circle"
    c1_start = x_coord-(semi_radius+circle_range) # start of the first curve
    c_start = x_coord-(semi_radius)# start of drawing the circle
    c2_start = x_coord+semi_radius # start of drawing the 2nd curve
    
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
    return c_points

hill_points = generate_hill_points(
    percent_semi_circle=0.9, 
    semi_radius=1, 
    y_coord=0, 
    x_coord=0, 
    hill_height=1, 
    num_points=1000
)
print(hill_points)
curve(pos=hill_points)

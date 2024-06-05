Web VPython 3.2

def generate_hill_points(percent_semi_circle, radius, hill_height, num_points, starting_pos=None, y_coord=0, x_coord=0):
    c_points = []
    circle_range = sqrt(radius) * percent_semi_circle # how much to the left and right to draw the "circle"
    c1_start = x_coord-(radius+circle_range) # start of the first curve
    c_start = x_coord-(circle_range)# start of drawing the circle
    c2_start = x_coord+circle_range # start of drawing the 2nd curve
    
    hill_width = (radius+circle_range)-c1_start
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
            
    return (c_points, {'x': x_coord + offset.x, 'y': y_coord + offset.y}, { 'start': c_start, 'end': c2_start })

def generate_left_curve(initial_height, num_points, starting_pos=None):
    c_points = []
    left_curve_amount = sqrt(initial_height)
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
    
    
def draw_line(p1, p2, num_points, starting_pos=None):
    slope = (p2 - p1)/(num_points - 1)
    ps = [p1]
    
    offset = vec(0, 0, 0)
    if starting_pos:
        offset = starting_pos - ps[0]
        ps[0] = starting_pos
        
    for i in range(1, num_points):
        ps.append(ps[i-1] + slope + offset)
            
    return ps

hill_radius = 1

def generate_cart_path():
    left = generate_left_curve(2, 10)
    line = draw_line(vec(0, 0, 0), vec(2, 0, 0), 10, starting_pos=left[-1])
    
    hill_points, center, circle_range = generate_hill_points(
            percent_semi_circle=0.96,
            radius=hill_radius,
            hill_height=2,
            num_points=150, starting_pos=line[-1]
        )
    
    
    
    return left+line + hill_points
    
cart_path = generate_cart_path()
path_curve = curve(pos=cart_path)

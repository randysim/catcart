Web VPython 3.2

def generate_hill_points(percent_semi_circle, semi_radius, y_coord, x_coord, hill_height, num_points):
    cx_range = semi_radius * percent_semi_circle # how much to the left and right to draw the "circle"
    c1_start = x_coord-(semi_radius+cx_range) # start of the first curve
    c_start = x_coord-(semi_radius)# start of drawing the circle
    c2_start = semi_radius # start of drawing the 2nd curve
    
    hill_width = (semi_radius+cx_range)-c1_start
    for i in range(num_points):
        percent_done = i/num_points # percent done with drawing
        cx = c1_start + (hill_width*percent_done) # 
        
        if (current

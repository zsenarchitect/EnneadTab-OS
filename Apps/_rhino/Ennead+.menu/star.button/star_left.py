__title__ = "MakeStar"





def star_left():
    print ("this is a star")
    import rhinoscriptsyntax as rs
    import math

    def draw_star(center, outer_radius, inner_radius, num_points):
        """
        Draw a star in Rhino.
        
        :param center: Tuple (x, y, z) - Center of the star
        :param outer_radius: float - Radius of the outer points
        :param inner_radius: float - Radius of the inner points
        :param num_points: int - Number of points of the star
        :return: None
        """
        angle_between_points = math.pi / num_points
        points = []

        for i in range(2 * num_points):
            angle = i * angle_between_points
            if i % 2 == 0:
                # Outer point
                x = center[0] + outer_radius * math.cos(angle)
                y = center[1] + outer_radius * math.sin(angle)
            else:
                # Inner point
                x = center[0] + inner_radius * math.cos(angle)
                y = center[1] + inner_radius * math.sin(angle)
            points.append((x, y, center[2]))

        star = rs.AddPolyline(points + [points[0]])
        return star

    # Example usage
    center_point = (0, 0, 0)
    outer_r = 10
    inner_r = 5
    points = 5
    return draw_star(center_point, outer_r, inner_r, points)
def rect_collision(r1, r2):
    return (
        r1.x < r2.x + r2.w and
        r1.x + r1.w > r2.x and
        r1.y < r2.y + r2.h and
        r1.y + r1.h > r2.y
    )

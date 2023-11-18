import svgwrite

def generate_smiling_chef_svg(output_path='smiling_chef.svg'):
    # Create SVG drawing
    dwg = svgwrite.Drawing(output_path, profile='tiny')

    # Draw a chef hat
    hat_color = 'black'
    hat_height = 70
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', hat_height), fill=hat_color))

    # Draw a smiling face
    face_radius = 100
    face_color = 'peachpuff'
    face_position = (150, hat_height + face_radius + 20)
    dwg.add(dwg.ellipse(center=face_position, r=(face_radius, face_radius), fill=face_color))

    # Draw eyes
    eye_radius = 10
    eye_color = 'black'
    eye_positions = [(120, face_position[1] - 20), (180, face_position[1] - 20)]
    for eye_position in eye_positions:
        dwg.add(dwg.ellipse(center=eye_position, r=(eye_radius, eye_radius), fill=eye_color))

    # Draw a smiling mouth
    smile_radius = 50
    dwg.add(dwg.path(d=f"M {face_position[0] - smile_radius},{face_position[1] + 30} "
                       f"A {smile_radius},{smile_radius} 0 0,1 {face_position[0] + smile_radius},{face_position[1] + 30}",
                     stroke=eye_color, fill='none', stroke_width=5))

    # Save the SVG
    dwg.save()

if __name__ == '__main__':
    generate_smiling_chef_svg()

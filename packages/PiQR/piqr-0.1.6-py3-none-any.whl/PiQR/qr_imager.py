import cv2
import numpy as np
import os
import math

def correct_orientation(input_data, qr_size, module_size):
    # Corrects the orientation of the QR code coordinates.
    new_coords = []
    for coords, state in input_data:
        x = coords[0]  # X-coordinate
        y = qr_size - coords[1]  # Flip Y-coordinate to match image orientation
        new_coords.append(((x, y), state))  # Append corrected coordinates with state
    return new_coords  # Return the list of new coordinates

def write_image(image, file_dir):
    # Saves the given image to the specified directory.
    if file_dir is None:
        # If no directory is specified, save to a default filename.
        cv2.imwrite('qr_image.png', image)
    else:
        try:
            # Attempt to save the image to the specified directory.
            cv2.imwrite(file_dir, image)
        except:
            # Raise an error if the directory does not exist.
            raise ValueError(f"{file_dir} Does Not Exist")

def create_qr_png(input_data, file_dir, code_shape='Square'):
    # Generates a QR code image based on input data and saves it to the specified directory.
    qr_size = int(math.sqrt(len(input_data)))  # Calculate the size of the QR code
    module_size = 1  # Size of each module in the QR code
    size_factor = 80  # Scaling factor for module size
    placement = 100  # Placement offset for the QR code in the image
    oriented_data = correct_orientation(input_data, qr_size, module_size)  # Correct the orientation

    # Calculate the overall width and height of the QR code image
    width = (qr_size * size_factor) + (placement * 2)
    height = width
    # Create a blank white image for the QR code
    qr_image = np.zeros([width + (module_size * size_factor) + placement, height, 3], dtype=np.uint8)
    #qr_image.fill(255)  # Fill the image with white color
    cv2.rectangle(qr_image, (0, 0), (width+(module_size*size_factor)+placement, width+(module_size*size_factor)+placement), (199, 199, 191), -1)

    # Draw the QR code modules on the image
    for coords, state in oriented_data:
        x, y = coords  # Get the coordinates
        # Calculate the corners of the module
        x1 = x * size_factor + placement - 50
        y1 = y * size_factor + placement
        x2 = (x + 1) * size_factor + placement - 50
        y2 = (y + 1) * size_factor + placement

        if state != 0:
            color = (0, 0, 0)  # Set color to black for filled modules
            # Draw either a circle or rectangle based on the code_shape parameter
            if code_shape == 'Circle':
                cv2.circle(qr_image, (x1 + (x2 - x1), y1 + (y2 - y1)), 40, color, thickness=-1)
            else:
                cv2.rectangle(qr_image, (x1 + 50, y1), (x2 + 50, y2), color, -1)

    # Resize the QR code image to a standard size for output
    bigger = cv2.resize(qr_image, (120, 120))
    write_image(bigger, file_dir)  # Save the generated image

def display_qr_image(input_data, code_shape):
    # Displays the QR code image in a window.
    alignment_data = []  # Initialize an empty list for alignment data
    module_size = 1  # Size of each module in the QR code
    size_factor = 80  # Scaling factor for module size
    qr_size = int(math.sqrt(len(input_data)))  # Calculate the size of the QR code
    placement = 100  # Placement offset for the QR code in the image
    oriented_data = correct_orientation(input_data, qr_size, module_size)  # Correct the orientation
    oriented_alignment = correct_orientation(alignment_data, qr_size, module_size)  # Correct alignment orientation

    # Calculate the overall width and height of the QR code image
    width = (qr_size * size_factor) + (placement * 2)
    height = width
    # Create a blank white image for the QR code
    qr_image = np.zeros([width + (module_size * size_factor) + placement, height, 3], dtype=np.uint8)
    qr_image.fill(255)  # Fill the image with white color

    # Draw the QR code modules on the image
    for coords, state in oriented_data:
        x, y = coords  # Get the coordinates
        # Calculate the corners of the module
        x1 = x * size_factor + placement - 50
        y1 = y * size_factor + placement
        x2 = (x + 1) * size_factor + placement - 50
        y2 = (y + 1) * size_factor + placement

        if state != 0:
            # Determine color based on whether the coordinates are part of the alignment data
            if coords in [i[0] for i in oriented_alignment]:
                color = (0, 255, 0)  # Set color to green for alignment modules
            else:
                color = (0, 0, 0)  # Set color to black for filled modules

            # Draw either a circle or rectangle based on the code_shape parameter
            if code_shape == 'Circle':
                cv2.circle(qr_image, (x1 + (x2 - x1), y1 + (y2 - y1)), 40, color, thickness=-1)
            else:
                cv2.rectangle(qr_image, (x1 + 50, y1), (x2 + 50, y2), color, -1)

    # Display the generated QR code image in a window
    cv2.imshow('QR', cv2.resize(qr_image, (600, 600)))
    cv2.waitKey(0)  # Wait indefinitely until a key is pressed
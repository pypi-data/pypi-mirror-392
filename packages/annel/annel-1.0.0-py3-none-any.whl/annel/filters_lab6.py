"""
Image Filters Implementation from Lab 6
Usage:
from filters_lab6 import apply_filters, plot_filter_results

# Apply filters
filters = {
    'edge': edge_filter,
    'vertical': vertical_filter, 
    'horizontal': horizontal_filter,
    'smoothing': smoothing_filter,
    'sharpening': sharpening_filter
}

results = apply_filters(image_array, filters)
plot_filter_results(results)
"""

import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Define filters
vertical_filter = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
horizontal_filter = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
smoothing_filter = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]) / 9.0
sharpening_filter = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
edge_filter = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])

def apply_filters(img_array, filters_dict):
    """
    Apply multiple filters to an image
    
    Args:
        img_array: numpy array of the image
        filters_dict: dictionary of filters {name: filter_array}
        
    Returns:
        dictionary of filtered images {name: filtered_image}
    """
    results = {}
    input_image = img_array.reshape((1, img_array.shape[0], img_array.shape[1], 1))
    
    for name, filter_array in filters_dict.items():
        # Reshape filter for CNN
        filter_reshaped = filter_array.reshape((3, 3, 1, 1))
        
        # Create model and apply filter
        model = models.Sequential()
        model.add(layers.Conv2D(1, (3, 3), input_shape=(img_array.shape[0], img_array.shape[1], 1)))
        model.layers[0].set_weights([filter_reshaped, np.array([0.0])])
        
        output = model.predict(input_image)
        results[name] = output[0, :, :, 0]
    
    return results

def plot_filter_results(original_img, filtered_results):
    """
    Plot original image and filtered results
    
    Args:
        original_img: original image array
        filtered_results: dictionary of filtered images from apply_filters
    """
    n_filters = len(filtered_results)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Plot original image
    axes[0, 0].imshow(original_img, cmap='gray')
    axes[0, 0].set_title('Original Image')
    axes[0, 0].axis('off')
    
    # Plot filtered images
    for idx, (name, filtered_img) in enumerate(filtered_results.items()):
        row = (idx + 1) // 3
        col = (idx + 1) % 3
        axes[row, col].imshow(filtered_img, cmap='gray')
        axes[row, col].set_title(name.title())
        axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.show()

def load_and_preprocess_image(image_path):
    """
    Load and preprocess image for filtering
    
    Args:
        image_path: path to the image file
        
    Returns:
        normalized image array
    """
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    img_array = np.array(img)
    img_array = img_array.astype('float32') / 255.0  # Normalize
    return img_array

# Example usage
if __name__ == "__main__":
    # Load image
    image_path = 'path/to/your/image.jpg'  # Replace with actual path
    img_array = load_and_preprocess_image(image_path)
    
    # Define filters dictionary
    filters = {
        'edge': edge_filter,
        'vertical': vertical_filter,
        'horizontal': horizontal_filter, 
        'smoothing': smoothing_filter,
        'sharpening': sharpening_filter
    }
    
    # Apply filters
    results = apply_filters(img_array, filters)
    
    # Plot results
    plot_filter_results(img_array, results)
    
    # Interpretation
    print("""
    Interpretation of Outputs:
    
    - Edge Detection Filter: Highlights edges and boundaries where intensity changes occur
    - Vertical Line Detection Filter: Shows stronger response to vertical lines and structures
    - Horizontal Line Detection Filter: Emphasizes horizontal lines and features  
    - Smoothing Filter: Reduces noise and blurs the image, producing softer output
    - Sharpening Filter: Enhances contrast around edges, making details more defined
    """)
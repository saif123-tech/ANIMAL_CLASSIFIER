"""
Dataset Management Utilities
Handles dataset operations like class extraction, validation, and statistics
"""

import os
from typing import List, Dict, Tuple
from PIL import Image, UnidentifiedImageError


def get_class_names_from_dataset(dataset_path: str = "dataset") -> List[str]:
    """
    Extract class names from dataset folder without loading images.
    
    Args:
        dataset_path: Path to the dataset folder
        
    Returns:
        List of class names (folder names)
    """
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset folder not found: {dataset_path}")
        return []
    
    class_names = []
    for item in os.listdir(dataset_path):
        item_path = os.path.join(dataset_path, item)
        if os.path.isdir(item_path):
            class_names.append(item)
    
    return sorted(class_names)


def validate_dataset(dataset_path: str = "dataset") -> Dict[str, int]:
    """
    Validate dataset and return statistics.
    
    Args:
        dataset_path: Path to the dataset folder
        
    Returns:
        Dictionary with class names as keys and image counts as values
    """
    class_names = get_class_names_from_dataset(dataset_path)
    stats = {}
    
    for class_name in class_names:
        class_path = os.path.join(dataset_path, class_name)
        valid_images = 0
        
        for file in os.listdir(class_path):
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                img_path = os.path.join(class_path, file)
                try:
                    with Image.open(img_path) as img:
                        img.convert("RGB")
                    valid_images += 1
                except (UnidentifiedImageError, OSError, SyntaxError):
                    print(f"[Warning] Corrupted image: {img_path}")
        
        stats[class_name] = valid_images
    
    return stats


def print_dataset_stats(dataset_path: str = "dataset"):
    """
    Print dataset statistics in a formatted way.
    
    Args:
        dataset_path: Path to the dataset folder
    """
    print("📊 Dataset Statistics")
    print("=" * 50)
    
    stats = validate_dataset(dataset_path)
    total_images = sum(stats.values())
    total_classes = len(stats)
    
    print(f"Total Classes: {total_classes}")
    print(f"Total Images: {total_images}")
    print(f"Average Images per Class: {total_images / total_classes:.1f}")
    print()
    
    print("📁 Class Breakdown:")
    for class_name, count in stats.items():
        print(f"  {class_name}: {count} images")
    
    print("=" * 50)


def get_minimum_images_per_class(dataset_path: str = "dataset", min_count: int = 10) -> List[str]:
    """
    Find classes with fewer than minimum required images.
    
    Args:
        dataset_path: Path to the dataset folder
        min_count: Minimum number of images required per class
        
    Returns:
        List of class names that need more images
    """
    stats = validate_dataset(dataset_path)
    insufficient_classes = []
    
    for class_name, count in stats.items():
        if count < min_count:
            insufficient_classes.append(class_name)
    
    return insufficient_classes


if __name__ == "__main__":
    # Example usage
    print_dataset_stats()
    
    # Check for classes with insufficient images
    insufficient = get_minimum_images_per_class(min_count=20)
    if insufficient:
        print(f"\n⚠️ Classes with fewer than 20 images: {insufficient}")
    else:
        print("\n✅ All classes have sufficient images") 
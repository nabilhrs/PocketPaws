import os
from PIL import Image, ImageDraw

def generate_placeholders():
    folder_path = "assets/images/items"
    os.makedirs(folder_path, exist_ok=True)

    items = {
        "meaty_chew.png": "#E2F0CB",     # Food (Green)
        "tuna_treat.png": "#E2F0CB",
        "carrot_stick.png": "#E2F0CB",
        "squeaky_bone.png": "#FFDEB4",   # Toys (Orange)
        "yarn_ball.png": "#FFDEB4",
        "willow_ball.png": "#FFDEB4",
        "antibiotics.png": "#FFB7B2",    # Medicine (Red)
        "energy_drink.png": "#C7CEEA",   # Energy (Blue)
        "revival_charm.png": "#F3E5AB"   # Charm (Gold)
    }

    for filename, color_hex in items.items():
        img = Image.new('RGB', (150, 150), color=color_hex)
        draw = ImageDraw.Draw(img)

        draw.rectangle([10, 10, 140, 140], outline="white", width=5)

        save_path = os.path.join(folder_path, filename)
        img.save(save_path)
        print(f"Created: {save_path}")

    print("\nAll 9 placeholder icons generated successfully!")

if __name__ == "__main__":
    generate_placeholders()